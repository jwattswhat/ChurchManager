import unittest
from pathlib import Path

import reset_worship_test_services as reset


class WorshipResetTests(unittest.TestCase):
    def test_cleanup_scope_contains_service_dependents(self):
        self.assertIn("tblService", reset.TABLES)
        self.assertIn("tblServiceRole", reset.TABLES)
        self.assertIn("tblHymnUsage", reset.TABLES)
        self.assertIn("tblServiceBulletinOrderLine", reset.TABLES)

    def test_script_is_hard_guarded_to_local_test_database(self):
        source = Path(reset.__file__).read_text(encoding="utf-8")
        self.assertIn('!= "churchdbtest"', source)
        self.assertIn('not in {"127.0.0.1", "localhost", "::1"}', source)
        self.assertIn("ChurchDBTest.pre-worship-reset", source)
        self.assertIn("cleanup_verified=true", source)


if __name__ == "__main__":
    unittest.main()
