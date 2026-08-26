import unittest

from accounting.starter_data import (
    STARTER_ACCOUNTS, STARTER_FUNDS, STARTER_FUNCTIONS,
)


class TestAccountingStarterData(unittest.TestCase):
    def test_account_codes_are_unique_and_follow_approved_ranges(self):
        codes = [account.code for account in STARTER_ACCOUNTS]
        self.assertEqual(len(codes), len(set(codes)))
        ranges = {
            "ASSET": range(1000, 2000), "LIABILITY": range(2000, 3000),
            "NET_ASSET": range(3000, 4000), "REVENUE": range(4000, 5000),
            "EXPENSE": range(5000, 8000), "TRANSFER": range(8000, 9000),
        }
        for account in STARTER_ACCOUNTS:
            self.assertIn(int(account.code), ranges[account.account_type])

    def test_modified_cash_accounts_begin_inactive(self):
        inactive = {account.code for account in STARTER_ACCOUNTS if not account.active}
        self.assertEqual(inactive, {"1200", "1590", "2000", "2300", "6000"})

    def test_special_funds_require_explicit_classification(self):
        classified = {fund.code for fund in STARTER_FUNDS if not fund.requires_classification}
        self.assertEqual(classified, {"GENERAL", "RESERVE"})
        reserve = next(fund for fund in STARTER_FUNDS if fund.code == "RESERVE")
        self.assertTrue(reserve.board_designated)
        self.assertFalse(next(f for f in STARTER_FUNDS if f.code == "ENDOWMENT").active)

    def test_supporting_functions_remain_distinct(self):
        classes = {function.code: function.function_class for function in STARTER_FUNCTIONS}
        self.assertEqual(classes["MGMT"], "MANAGEMENT_GENERAL")
        self.assertEqual(classes["FUNDRAISING"], "FUNDRAISING")


if __name__ == "__main__":
    unittest.main()
