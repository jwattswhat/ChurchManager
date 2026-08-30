"""Contract tests for guarded, non-approving GUI visual candidates."""

import unittest
from unittest import mock

import generate_gui_visual_candidates as candidates
from JSForm.gui_testing import GUITestError


class GUIVisualProfileTests(unittest.TestCase):
    def test_profile_records_required_environment_and_unapproved_state(self):
        profile = candidates.display_profile()
        self.assertEqual(profile["profile"], "gui-visual")
        self.assertEqual(profile["baseline_status"], "candidate-unapproved")
        self.assertIn("ppi", profile)
        self.assertIn("display_pixels", profile)

    def test_incompatible_scaling_fails_before_capture(self):
        with mock.patch.object(candidates, "display_profile", return_value={"ppi": [120, 120]}), \
             mock.patch.object(candidates, "capture_client") as capture:
            with self.assertRaisesRegex(RuntimeError, "Visual profile unavailable"):
                candidates.main()
            capture.assert_not_called()

    def test_capture_failure_is_recorded_as_environment_incompatible(self):
        compatible = {
            "profile": "gui-visual", "ppi": [96, 96],
            "baseline_status": "candidate-unapproved",
        }
        with mock.patch.object(candidates, "display_profile", return_value=compatible), \
             mock.patch.object(candidates, "capture_client", side_effect=GUITestError("black capture")), \
             mock.patch.object(candidates.Path, "write_text", autospec=True):
            self.assertEqual(candidates.main(), 2)
        self.assertEqual(compatible["baseline_status"], "environment-incompatible")

    def test_manual_review_presents_every_screen_without_capture(self):
        window = mock.Mock()
        window.GetSize.return_value = mock.Mock(width=900, height=700)
        definitions = (("example", lambda: window, (800, 600)),)
        with mock.patch.object(candidates, "WINDOWS", definitions), \
             mock.patch.object(candidates, "capture_client") as capture, \
             mock.patch.object(candidates, "drain_events"):
            self.assertEqual(candidates.main(review=True), 0)
        window.SetSize.assert_called_once_with((900, 700))
        window.CentreOnScreen.assert_called_once_with()
        window.ShowModal.assert_called_once_with()
        window.Destroy.assert_called_once_with()
        capture.assert_not_called()

    def test_review_size_never_shrinks_a_fitted_dialog(self):
        window = mock.Mock()
        window.GetSize.return_value = mock.Mock(width=510, height=480)
        candidates.apply_review_size(window, (520, 430))
        window.SetSize.assert_called_once_with((520, 480))


if __name__ == "__main__":
    unittest.main()
