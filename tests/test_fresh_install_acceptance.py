import unittest
from datetime import datetime
from unittest.mock import patch

import accept_fresh_install_baseline as acceptance


class Cursor:
    def __init__(self):
        self.executed = []
        self.closed = False

    def execute(self, sql, values=None):
        self.executed.append((sql, values))

    def close(self):
        self.closed = True


class Connection:
    def __init__(self):
        self.value = Cursor()

    def cursor(self):
        return self.value


class FreshInstallAcceptanceTests(unittest.TestCase):
    def test_names_are_disposable_and_deterministic_for_test_clock(self):
        database, account = acceptance.disposable_names(datetime(2026, 8, 17, 9, 30, 2))
        self.assertEqual(database, "CMFreshAcceptance_20260817093002")
        self.assertEqual(account, "cm_accept_20260817093002")

    def test_cleanup_refuses_any_nondisposable_database(self):
        with self.assertRaisesRegex(acceptance.FreshInstallAcceptanceError, "unrecognized database"):
            acceptance._drop_disposable(Connection(), "ChurchDBTest", "cm_accept_20260817093002")

    def test_cleanup_refuses_any_nondisposable_account(self):
        with self.assertRaisesRegex(acceptance.FreshInstallAcceptanceError, "unrecognized account"):
            acceptance._drop_disposable(Connection(), "CMFreshAcceptance_20260817093002", "church")

    def test_cleanup_targets_only_exact_generated_identifiers(self):
        connection = Connection()
        acceptance._drop_disposable(
            connection, "CMFreshAcceptance_20260817093002", "cm_accept_20260817093002",
        )
        statements = [sql for sql, _values in connection.value.executed]
        self.assertEqual(statements, [
            "DROP USER IF EXISTS 'cm_accept_20260817093002'@'127.0.0.1'",
            "DROP DATABASE IF EXISTS `CMFreshAcceptance_20260817093002`",
        ])
        self.assertTrue(connection.value.closed)

    def test_preview_never_prompts_or_connects(self):
        with patch("accept_fresh_install_baseline.getpass.getpass") as prompt:
            self.assertEqual(acceptance.main([]), 0)
        prompt.assert_not_called()


if __name__ == "__main__":
    unittest.main()
