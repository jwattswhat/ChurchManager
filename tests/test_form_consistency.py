"""Static consistency checks for ChurchManager JSON screen definitions."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / "Forms"


def load_forms():
    for path in sorted(FORMS.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        root_key = next(iter(document))
        if root_key.casefold() != (path.stem + "FORM").casefold():
            raise AssertionError(f"{path.name}: unexpected root key {root_key}")
        yield path, root_key, document[root_key]


class FormConsistencyTests(unittest.TestCase):
    def test_control_dictionary_keys_match_control_names(self):
        mismatches = []
        for path, _, form in load_forms():
            for key, control in form.get("CONTROLS", {}).items():
                name = control.get("name")
                if name and name != key:
                    mismatches.append(f"{path.name}: {key} != {name}")
        self.assertEqual(mismatches, [])

    def test_address_and_event_dates_use_standard_native_controls(self):
        expected = {
            "frmFamilyAddress": {"StartDate": "DatePickerCtrl", "EndDate": "DatePickerCtrl"},
            "frmPersonAddress": {"StartDate": "DatePickerCtrl", "EndDate": "DatePickerCtrl"},
            "frmFamilyDate": {"Date": "DatePickerCtrl"},
            "frmPersonDate": {"Date": "DatePickerCtrl"},
            "frmAttendanceEvent": {"DateTime": "DateTime"},
        }
        forms = {path.stem: form for path, _, form in load_forms()}
        for form_name, fields in expected.items():
            controls = forms[form_name]["CONTROLS"]
            for field_name, control_type in fields.items():
                with self.subTest(form=form_name, field=field_name):
                    self.assertEqual(controls[field_name]["type"], control_type)
                    width = controls[field_name].get("sizech", [20])[0]
                    self.assertLessEqual(width, 20)

    def test_common_user_facing_labels_use_standard_spelling(self):
        obsolete_labels = {"eMail:", "Zip:", "DocumentType:", "CheckList:", "CheckLists"}
        found = []
        for path, _, form in load_forms():
            for key, control in form.get("CONTROLS", {}).items():
                if control.get("label") in obsolete_labels:
                    found.append(f"{path.name}: {key} = {control['label']}")
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
