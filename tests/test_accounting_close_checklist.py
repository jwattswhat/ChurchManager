from pathlib import Path
import unittest

from accounting.close_checklist_service import check


class CloseChecklistTests(unittest.TestCase):
    def test_check_reports_clear_or_blocked_with_specific_detail(self):
        clear=check("Drafts",0,"None remain","Drafts remain")
        blocked=check("Drafts",2,"None remain","Two remain")
        self.assertEqual(clear,{"check":"Drafts","status":"CLEAR","detail":"None remain"})
        self.assertEqual(blocked,{"check":"Drafts","status":"BLOCKED","detail":"Two remain"})

    def test_menu_is_report_protected_and_service_checks_required_controls(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingCloseChecklist",SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingCloseChecklist"],
                         "accounting.reports.run")
        source=(Path(__file__).parents[1]/"accounting"/"close_checklist_service.py").read_text(encoding="utf-8-sig")
        for phrase in ("Unposted transactions","Required source documents",
                       "Unmatched bank activity","Draft reconciliations",
                       "Completed bank statements","Ledger balance"):
            self.assertIn(phrase,source)


if __name__=="__main__":unittest.main()
