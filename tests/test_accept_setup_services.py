import unittest
from datetime import datetime

from accept_setup_services import acceptance_names, plan_for
from installation_readiness import CatalogPackage, ReadinessReport


class SetupServiceAcceptanceTests(unittest.TestCase):
    def test_disposable_names_are_bounded_and_identifiable(self):
        database, account = acceptance_names(datetime(2026, 8, 17, 12, 0, 0))
        self.assertEqual(database, "CMSetupAcceptance_20260817120000")
        self.assertEqual(account, "cm_setup_20260817120000")
        self.assertLessEqual(len(account), 32)

    def test_acceptance_plan_selects_distributable_lectionary(self):
        package = CatalogPackage(
            "lectionary", "public-cycle", "Public Cycle", "1.0.0",
            None, True, True, "Validated.", None,
        )
        plan = plan_for("CMSetupAcceptance_20260817120000", ReadinessReport((), (package,)))
        self.assertEqual(plan.lectionary_packages if hasattr(plan, "lectionary_packages") else
                         tuple(item.code for item in plan.selected_packages), ("public-cycle",))
        self.assertEqual(plan.default_lectionary, "public-cycle")


if __name__ == "__main__":
    unittest.main()
