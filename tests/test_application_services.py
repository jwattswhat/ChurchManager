from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from backup_service import BackupService
from process_service import ProcessService
from report_service import ChurchManagerReportService


class TestProcessService(unittest.TestCase):
    def test_python_report_uses_current_runtime_and_argument_list(self):
        calls = []
        service = ProcessService(popen=lambda command: calls.append(command), python_executable="python.exe")
        service.start_python("report.py", ["--test"])
        self.assertEqual(calls, [["python.exe", "report.py", "--test"]])


class TestBackupService(unittest.TestCase):
    def test_password_is_kept_out_of_process_arguments(self):
        calls = []
        class FixedClock:
            @staticmethod
            def strftime(_format):
                return "2026-08-10.1200"
        def runner(command, stdout, check):
            calls.append(command)
            stdout.write(b"backup")
        with tempfile.TemporaryDirectory() as folder:
            prefix = str(Path(folder) / "backup")
            result = BackupService(runner=runner, clock=lambda: FixedClock()).create(
                {"server": "db", "database": "ChurchDBTest", "user": "church", "password": "secret"},
                folder, prefix,
            )
            self.assertTrue(result.path.exists())
            self.assertNotIn("secret", " ".join(calls[0]))


class TestReportService(unittest.TestCase):
    def test_catalog_reports_stay_on_jsform(self):
        checked = []
        class JSFormStub:
            @staticmethod
            def RunReport(*arguments):
                return arguments
        class AccessStub:
            @staticmethod
            def require_report(report_id):
                checked.append(report_id)
        settings = {"database": "ChurchDBTest"}
        service = ChurchManagerReportService(
            JSFormStub, object(), AccessStub(), connection_settings=settings
        )
        self.assertEqual(
            service.run_catalog_report(7, "form", "connection"),
            (7, "form", "connection", settings),
        )
        self.assertEqual(checked, [7])


if __name__ == "__main__":
    unittest.main()
