import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BackupRestoreWorkflowTests(unittest.TestCase):
    def test_restore_permission_is_sensitive_and_master_only_by_default(self):
        migration = (ROOT / "migrations" / "051_add_database_restore_permission.sql").read_text()
        self.assertIn("application.database.restore", migration)
        self.assertIn("Master Administrator", migration)

    def test_restore_requires_confirmation_and_pre_restore_backup(self):
        dialog = (ROOT / "backup_restore_dialog.py").read_text()
        service = (ROOT / "backup_service.py").read_text()
        self.assertIn('authorization.require("application.database.restore"', dialog)
        self.assertIn("Type the active database name", dialog)
        self.assertIn("safety = self.create_in_folder", service)
        self.assertIn("The pre-restore backup was preserved", service)

    def test_clean_exit_backup_is_once_per_day(self):
        source = (ROOT / "backup_restore_dialog.py").read_text()
        self.assertIn('values["last_automatic_date"]==current', source)
        self.assertIn('values["last_automatic_date"]=current', source)

    def test_restore_does_not_put_password_on_command_line(self):
        source = (ROOT / "backup_service.py").read_text()
        restore = source.split("def restore", 1)[1]
        self.assertIn("--defaults-extra-file=", restore)
        self.assertNotIn('settings["password"]]', restore)

    def test_tools_folder_can_recover_from_stale_configuration(self):
        source = (ROOT / "backup_restore_dialog.py").read_text()
        self.assertIn('glob("MariaDB */bin")', source)
        self.assertIn('"mariadb-dump"', source)

    def test_restore_displays_a_working_message(self):
        source = (ROOT / "backup_restore_dialog.py").read_text()
        self.assertIn("Restoring the ChurchManager database", source)
        self.assertIn("Do not close the program", source)
        self.assertIn("wx.BusyInfo", source)

    def test_restore_releases_live_connections_before_import(self):
        source = (ROOT / "backup_restore_dialog.py").read_text()
        tools_position = source.index("tools_directory = mariadb_tools_directory(self.jsform)")
        close_position = source.index("close_database_connections(self.context)")
        restore_position = source.index("self.context.services.backups.restore(")
        self.assertLess(tools_position, close_position)
        self.assertLess(close_position, restore_position)
        self.assertIn("self.context.settings,tools_directory,path,backup_folder", source)
        self.assertIn('("DBConnection", "JSConnection")', source)
        self.assertIn("must restart because its database connections were closed", source)

    def test_pastoral_recovery_password_is_requested_before_database_close(self):
        source = (ROOT / "backup_restore_dialog.py").read_text()
        prompt = source.index("wx.PasswordEntryDialog")
        close = source.index("close_database_connections(self.context)")
        restore = source.index("self.context.services.backups.restore(")
        self.assertLess(prompt, close)
        self.assertLess(close, restore)
        self.assertIn("recovery_password=recovery_password", source)


if __name__ == "__main__":
    unittest.main()
