import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import JSForm
from cm import clsForm

from file_opening_policy import (
    PASSIVE_DOCUMENT_EXTENSIONS,
    configure_churchmanager_file_opening,
    configured_document_roots,
    normalize_picker_directory,
)


class FakeConfig:
    def __init__(self, values):
        self.values = values

    def get_Config_Value(self, family, key):
        return self.values.get((family, key))


class RaisingConfig:
    def get_Config_Value(self, _family, _key):
        raise RuntimeError("configuration table unavailable")


class FakeJSForm:
    def __init__(self, rejection=None):
        self.calls = []
        self.rejection = rejection

    def configure_file_opening(self, *args):
        self.calls.append(args)
        if args and self.rejection:
            raise self.rejection("unsafe root")
        return args or None


class FakePicker:
    def __init__(self, path):
        self.path = path


class FakeButton:
    def GetName(self):
        return "btnOpen"


class FakeEvent:
    def GetEventObject(self):
        return FakeButton()


class ChurchManagerFileOpeningPolicyTests(unittest.TestCase):
    def test_churchmanager_form_normalizes_picker_then_delegates_to_jsform(self):
        form = clsForm.__new__(clsForm)
        picker = FakePicker("Documents")
        form.CONTROLDESCRIPTION = {
            "btnOpen": {"action": ["openfile", "Document"]},
            "Document": {"type": "FilePickerCtrl"},
        }
        form.CONTROLID = {"Document": picker}
        with patch.object(JSForm.clsForm, "_openfileevent", return_value="delegated") as parent:
            result = form._openfileevent(FakeEvent())

        self.assertEqual(result, "delegated")
        self.assertTrue(Path(picker.path).is_absolute())
        parent.assert_called_once()

    def test_normalizes_legacy_relative_picker_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            picker = FakePicker("Documents")

            result = normalize_picker_directory(picker, folder)

            self.assertEqual(result, (Path(folder) / "Documents").resolve())
            self.assertEqual(Path(picker.path), result)

    def test_preserves_absolute_picker_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            picker = FakePicker(folder)

            result = normalize_picker_directory(picker, Path(folder).parent)

            self.assertEqual(result, Path(folder))
            self.assertEqual(picker.path, folder)

    def test_collects_document_sermon_and_outline_roots(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            for name in ("Documents", "Sermons", "Outlines"):
                (base / name).mkdir()
            config = FakeConfig({
                ("Location", "Document"): "Documents",
                ("Location", "Sermon"): str(base / "Sermons"),
                ("Location", "Outline"): "Outlines",
            })

            roots = configured_document_roots(config, base)

            self.assertEqual(roots, tuple((base / name).resolve() for name in (
                "Documents", "Sermons", "Outlines",
            )))

    def test_missing_and_duplicate_locations_are_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            documents = base / "Documents"
            documents.mkdir()
            config = FakeConfig({
                ("Location", "Document"): str(documents),
                ("Location", "Sermon"): str(documents),
                ("Location", "Outline"): str(base / "Missing"),
            })

            self.assertEqual(configured_document_roots(config, base), (documents.resolve(),))

    def test_remote_location_is_rejected_before_any_filesystem_probe(self):
        config = FakeConfig({("Location", "Document"): r"\\server\documents"})

        with patch.object(Path, "is_dir", side_effect=AssertionError("filesystem touched")):
            roots = configured_document_roots(config, Path.cwd())

        self.assertEqual(roots, ())

    def test_configures_only_documented_passive_types(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = FakeConfig({("Location", "Document"): str(root)})
            jsform = FakeJSForm()

            configure_churchmanager_file_opening(jsform, config, root)

            self.assertEqual(jsform.calls, [((root.resolve(),), PASSIVE_DOCUMENT_EXTENSIONS)])
            self.assertEqual(PASSIVE_DOCUMENT_EXTENSIONS, {".doc", ".docx", ".pdf", ".txt"})

    def test_no_valid_location_keeps_jsform_deny_all(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = FakeConfig({("Location", "Document"): str(root / "Missing")})
            jsform = FakeJSForm()

            result = configure_churchmanager_file_opening(jsform, config, root)

            self.assertIsNone(result)
            self.assertEqual(jsform.calls, [()])

    def test_missing_configuration_table_keeps_jsform_deny_all(self):
        with tempfile.TemporaryDirectory() as folder:
            jsform = FakeJSForm()

            configure_churchmanager_file_opening(jsform, RaisingConfig(), folder)

            self.assertEqual(jsform.calls, [()])

    def test_jsform_rejection_keeps_deny_all_and_does_not_abort_startup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            jsform = FakeJSForm(rejection=ValueError)

            result = configure_churchmanager_file_opening(
                jsform, FakeConfig({("Location", "Document"): str(root)}), root,
            )

            self.assertIsNone(result)
            self.assertEqual(jsform.calls[-1], ())

    def test_filesystem_policy_error_keeps_deny_all(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            jsform = FakeJSForm(rejection=PermissionError)

            result = configure_churchmanager_file_opening(
                jsform, FakeConfig({("Location", "Document"): str(root)}), root,
            )

            self.assertIsNone(result)
            self.assertEqual(jsform.calls[-1], ())


if __name__ == "__main__":
    unittest.main()
