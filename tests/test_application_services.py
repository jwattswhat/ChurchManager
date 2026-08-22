from datetime import datetime
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from backup_service import BackupError, BackupPreferences, BackupService
from process_service import ProcessService
from report_service import ChurchManagerReportService


class TestProcessService(unittest.TestCase):
    def test_python_report_uses_current_runtime_and_argument_list(self):
        calls = []
        service = ProcessService(popen=lambda command: calls.append(command), python_executable="python.exe")
        service.start_python("report.py", ["--test"])
        self.assertEqual(calls, [["python.exe", "report.py", "--test"]])

    def test_open_file_requests_a_visible_windows_application(self):
        calls = []

        def opener(*args, **kwargs):
            calls.append((args, kwargs))

        ProcessService(opener=opener).open_file("report.pdf")
        self.assertEqual(calls, [(("report.pdf", "open"), {"show_cmd": 5})])

    def test_open_file_supports_simple_injected_openers(self):
        calls = []
        ProcessService(opener=lambda path: calls.append(path)).open_file("report.pdf")
        self.assertEqual(calls, ["report.pdf"])


class TestBackupService(unittest.TestCase):
    class RecoveryStub:
        @staticmethod
        def sidecar_path(path):
            return Path(str(path) + ".PastoralRecovery.json")

        @staticmethod
        def attach_to_backup(_path):
            return None

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
            (Path(folder) / "mysqldump.exe").write_bytes(b"")
            prefix = str(Path(folder) / "backup")
            result = BackupService(runner=runner, clock=lambda: FixedClock()).create(
                {"server": "db", "database": "ChurchDBTest", "user": "church", "password": "secret"},
                folder, prefix,
            )
            self.assertTrue(result.path.exists())
            self.assertTrue(result.path.read_bytes().endswith(b"backup"))
            self.assertNotIn("secret", " ".join(calls[0]))
            self.assertEqual(BackupService.inspect_dump(result.path), "ChurchDBTest")

    def test_unrecognized_dump_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "unknown.sql"
            path.write_text("DROP DATABASE ChurchDB;", encoding="utf-8")
            with self.assertRaises(BackupError):
                BackupService.inspect_dump(path)

    def test_backup_preferences_survive_database_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "preferences.json"
            store = BackupPreferences(path)
            values = store.load()
            values.update(folder="D:/Church Backups", automatic_on_exit=False,
                          last_automatic_date="2026-08-14")
            store.save(values)
            self.assertEqual(store.load(), values)

    def test_backup_preferences_fall_back_when_windows_blocks_replace(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "preferences.json"
            path.write_text('{"folder": "old"}', encoding="utf-8")
            store = BackupPreferences(path)
            values = store.load()
            values["folder"] = "new"
            with mock.patch.object(Path, "replace", side_effect=PermissionError("locked")):
                store.save(values)
            self.assertEqual(store.load()["folder"], "new")

    def test_only_automatic_backups_are_pruned(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for number in range(4):
                (root / f"Automatic.ChurchDBTest.Backup.{number}.SQL").write_text("backup")
            manual = root / "Manual.ChurchDBTest.Backup.keep.SQL"
            manual.write_text("manual")
            BackupService.prune_automatic(root, "ChurchDBTest", keep=2)
            self.assertEqual(len(list(root.glob("Automatic.*.SQL"))), 2)
            self.assertTrue(manual.exists())

    def test_folder_backup_uses_readable_nonduplicated_name(self):
        calls = []
        class FixedClock:
            @staticmethod
            def strftime(_format):
                return "2026-08-14.1200"
        def runner(command, stdout, check):
            calls.append(command)
            stdout.write(b"backup")
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "mysqldump.exe").write_bytes(b"")
            result = BackupService(runner=runner, clock=lambda: FixedClock()).create_in_folder(
                {"server": "db", "database": "ChurchDBTest", "user": "church", "password": "secret"},
                folder, folder, automatic=True,
            )
            self.assertEqual(result.path.name, "Automatic.ChurchDBTest.Backup.2026-08-14.1200.SQL")

    def test_configured_port_is_used_by_backup(self):
        calls = []
        def runner(command, stdout, check):
            calls.append(command)
            stdout.write(b"backup")
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "mysqldump.exe").write_bytes(b"")
            BackupService(runner=runner).create(
                {"server": "db", "port": 3307, "database": "ChurchDBTest",
                 "user": "church", "password": "secret"},
                folder, str(Path(folder) / "backup"),
            )
            self.assertIn("--port", calls[0])
            self.assertIn("3307", calls[0])

    def test_mariadb_dump_name_is_accepted_when_mysqldump_is_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / "mariadb-dump.exe"
            executable.write_bytes(b"")
            self.assertEqual(
                BackupService._tool(folder, "mysqldump", "mariadb-dump"), executable
            )

    def test_prune_recognizes_older_duplicated_automatic_names(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for number in range(3):
                (root / f"ChurchDBTest.Automatic.ChurchDBTest.Backup.{number}.SQL").write_text("backup")
            BackupService.prune_automatic(root, "ChurchDBTest", keep=1)
            self.assertEqual(len(list(root.glob("ChurchDBTest.Automatic.*.SQL"))), 1)

    def test_restricted_notes_require_the_matching_recovery_sidecar(self):
        with tempfile.TemporaryDirectory() as folder:
            dump = Path(folder) / "backup.sql"
            dump.write_text(
                "-- ChurchManager database backup\n-- Database: ChurchDBTest\n"
                "INSERT INTO `tblPastoralRestrictedNote` VALUES (...);\n",
                encoding="utf-8",
            )
            service = BackupService(recovery=self.RecoveryStub())
            with self.assertRaisesRegex(BackupError, "recovery package is missing"):
                service.restore(
                    {"server": "db", "database": "ChurchDBTest", "user": "church",
                     "password": "secret"},
                    folder, dump, folder,
                )

    def test_pruning_an_automatic_backup_prunes_its_recovery_sidecar(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            keep = root / "Automatic.ChurchDBTest.Backup.2.SQL"
            obsolete = root / "Automatic.ChurchDBTest.Backup.1.SQL"
            for path in (keep, obsolete):
                path.write_text("backup", encoding="utf-8")
                Path(str(path) + ".PastoralRecovery.json").write_text(
                    "protected", encoding="utf-8"
                )
            keep.touch()
            BackupService.prune_automatic(root, "ChurchDBTest", keep=1)
            self.assertTrue(Path(str(keep) + ".PastoralRecovery.json").exists())
            self.assertFalse(Path(str(obsolete) + ".PastoralRecovery.json").exists())

    def test_restore_failure_detail_reports_code_and_redacts_quoted_data(self):
        error = subprocess.CalledProcessError(
            1, ["mariadb"],
            stderr=b"ERROR 1062 (23000) at line 44: Duplicate entry 'Private Name' for key 'uq_name'\n",
        )
        detail = BackupService._restore_failure_detail(error)
        self.assertIn("ERROR 1062", detail)
        self.assertIn("line 44", detail)
        self.assertNotIn("Private Name", detail)
        self.assertNotIn("uq_name", detail)


class TestReportService(unittest.TestCase):
    def test_catalog_report_without_visual_definition_fails_closed(self):
        checked = []
        class AccessStub:
            @staticmethod
            def require_report(report_id):
                checked.append(report_id)
                return ("LEGACY01", "reports.general.run")
        service = ChurchManagerReportService(
            object(), object(), AccessStub(), connection_settings={"database": "ChurchDBTest"}
        )
        with self.assertRaisesRegex(ValueError, "no approved JSForm visual definition"):
            service.run_catalog_report(7, "form", "connection")
        self.assertEqual(checked, [7])

    def test_official_visual_report_uses_visual_pipeline(self):
        class AccessStub:
            authorization = object()
            @staticmethod
            def require_report(report_id):
                return ("CMAS01", "reports.general.run")
        service = ChurchManagerReportService(object(), object(), AccessStub())
        service._run_visual_report = lambda code, form, connection: (code, form, connection)
        self.assertEqual(
            service.run_catalog_report(26, "form", "connection"),
            ("CMAS01", "form", "connection"),
        )


if __name__ == "__main__":
    unittest.main()
