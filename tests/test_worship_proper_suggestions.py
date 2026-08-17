"""Contract tests for explicit Proper suggestions in Worship Service."""

import json
from pathlib import Path
import unittest


class WorshipProperSuggestionTests(unittest.TestCase):
    def test_church_form_can_select_primary_edition(self):
        form = json.loads(Path("Forms/frmChurch.json").read_text(encoding="utf-8"))
        controls = form["frmChurchFORM"]["CONTROLS"]
        field = controls["PrimaryLectionaryEditionID"]
        self.assertEqual(field["lookupchoices"]["name"], "tblLectionaryEdition")
        self.assertTrue(field["lookupchoices"]["allowblank"])

    def test_worship_editor_requires_review_and_never_auto_selects_first_candidate(self):
        source = Path("unified_worship_service_dialog.py").read_text(encoding="utf-8")
        self.assertIn('label="Suggest Proper..."', source)
        self.assertIn("ProperCandidateDialog", source)
        self.assertIn("will not choose precedence", source)
        self.assertNotIn("candidates[0].proper_id", source)


if __name__ == "__main__":
    unittest.main()
