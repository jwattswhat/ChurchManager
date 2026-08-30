"""Safety tests for the explicit rollback-only GUI database profile."""

import unittest

from run_gui_database_profile import validate_target


class GUIDatabaseProfileTests(unittest.TestCase):
    def test_only_local_churchdbtest_and_test_credential_are_allowed(self):
        validate_target({"server": "127.0.0.1", "database": "ChurchDBTest",
                         "credential_target": "ChurchManager/LocalTestAdmin"})

    def test_production_remote_and_unknown_targets_fail_closed(self):
        cases = (
            {"server": "127.0.0.1", "database": "ChurchDB",
             "credential_target": "ChurchManager/LocalTestAdmin"},
            {"server": "192.168.3.200", "database": "ChurchDBTest",
             "credential_target": "ChurchManager/LocalTestAdmin"},
            {"server": "127.0.0.1", "database": "ChurchDBTest",
             "credential_target": "ChurchManager/Production"},
        )
        for settings in cases:
            with self.subTest(settings=settings), self.assertRaisesRegex(RuntimeError, "Safety stop"):
                validate_target(settings)


if __name__ == "__main__":
    unittest.main()
