import unittest
from pathlib import Path


class TestAccountingRegister(unittest.TestCase):
    def test_register_is_read_only_and_permission_protected(self):
        root = Path(__file__).parents[1]
        source = (root / "accounting" / "register_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn('title="Posted Transaction Register"', source)
        self.assertIn("Transaction lines (read only)", source)
        self.assertIn('authorization.require("accounting.transactions.view"', source)
        self.assertNotIn("Post Transaction", source)
        self.assertNotIn("Add Line", source)

    def test_register_query_excludes_unposted_transactions(self):
        root = Path(__file__).parents[1]
        source = (root / "accounting" / "register_service.py").read_text(encoding="utf-8-sig")
        self.assertIn("t.Status IN ('POSTED','REVERSED')", source)
        self.assertIn("TransactionNumber", source)


if __name__ == "__main__": unittest.main()
