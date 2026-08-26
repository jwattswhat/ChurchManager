import subprocess
import unittest
from unittest.mock import patch

from generate_installation_baseline import dump_schema


class GenerateInstallationBaselineTests(unittest.TestCase):
    @patch("generate_installation_baseline.find_mariadb_tool", return_value="mariadb-dump.exe")
    def test_dump_is_structure_only_and_password_is_not_an_argument(self, _tool):
        captured = {}

        def runner(command, **keywords):
            captured["command"] = command
            captured["keywords"] = keywords
            return subprocess.CompletedProcess(command, 0, b"CREATE TABLE sample (ID int);", b"")

        result = dump_schema({
            "server": "127.0.0.1", "port": 3306, "database": "ChurchDBTest",
            "user": "church", "password": "private-value",
        }, runner=runner)
        self.assertIn("CREATE TABLE", result)
        self.assertIn("--no-data", captured["command"])
        self.assertIn("--routines", captured["command"])
        self.assertNotIn("private-value", " ".join(captured["command"]))
        self.assertTrue(captured["keywords"]["check"])


if __name__ == "__main__":
    unittest.main()
