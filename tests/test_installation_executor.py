import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from installation_executor import (
    FreshInstallationExecutor,
    InstallationExecutionError,
)
from installation_plan import InstallationPlan


class Connection:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True

    def commit(self):
        pass


class InstallationExecutorTests(unittest.TestCase):
    def plan(self):
        return InstallationPlan(
            "Grace Lutheran Church", "ChurchManager_Grace", "admin",
            "Administrator", (), None, None,
        )

    def test_first_edition_is_deterministic(self):
        package = {"systems": [{"editions": [
            {"edition_key": "first"}, {"edition_key": "second"},
        ]}]}
        self.assertEqual(FreshInstallationExecutor._first_edition_key(package), "first")
        with self.assertRaisesRegex(InstallationExecutionError, "no edition"):
            FreshInstallationExecutor._first_edition_key({"systems": []})

    @patch("installation_executor.InitialMasterBootstrapper")
    @patch("installation_executor.InitialBackupVerifier")
    @patch("installation_executor.MigrationService")
    @patch("installation_executor.BaselineInstaller")
    @patch("installation_executor.load_seed", return_value=("seed", {}))
    @patch("installation_executor.load_baseline", return_value=("schema", {}))
    @patch("installation_executor.FreshDatabaseProvisioner")
    def test_orchestrates_verified_fresh_install(
        self, provisioner, _baseline_load, _seed_load, baseline_installer,
        migrations, backup, master,
    ):
        provisioner.return_value.create.return_value = object()
        baseline_installer.return_value.install.return_value = {
            "database_objects": 138,
            "represented_migrations": 84,
            "active_permissions": 43,
        }
        migrations.return_value.run.return_value = type(
            "MigrationResult", (), {"pending": (), "newly_applied": ()},
        )()
        master.return_value.create.return_value = 1
        backup.return_value.create.return_value = type(
            "Proof", (), {
                "path": Path("first.sql"), "size_bytes": 2048, "sha256": "a" * 64,
            },
        )()
        connection = Connection()
        executor = FreshInstallationExecutor(
            Mock(), lambda **_values: connection, root=Path(tempfile.gettempdir()),
        )
        executor._create_church = Mock(return_value=2)
        executor._install_packages = Mock(return_value=[])
        executor._verify = Mock()
        result = executor.install(
            self.plan(), "cm_grace", "a" * 20, "long master password", "long master password",
            dump_directory=Path("tools"), backup_folder=Path("backups"),
        )
        self.assertEqual((result.church_id, result.master_user_id), (2, 1))
        self.assertTrue(connection.closed)
        executor._verify.assert_called_once()

    def test_rejects_unvalidated_plan(self):
        executor = FreshInstallationExecutor(Mock(), Mock())
        with self.assertRaisesRegex(InstallationExecutionError, "plan is invalid"):
            executor.install(
                object(), "account", "x" * 20, "password", "password",
                dump_directory=Path("tools"), backup_folder=Path("backups"),
            )

    @patch("installation_executor.FreshDatabaseProvisioner")
    def test_failure_reports_stage_and_redacts_password(self, provisioner):
        provisioner.return_value.create.side_effect = RuntimeError(
            "database rejected secret-application-password"
        )
        executor = FreshInstallationExecutor(Mock(), Mock())
        with self.assertRaises(InstallationExecutionError) as caught:
            executor.install(
                self.plan(), "cm_grace", "secret-application-password",
                "secret-master-password", "secret-master-password",
                dump_directory=Path("tools"), backup_folder=Path("backups"),
            )
        message = str(caught.exception)
        self.assertIn("creating the ChurchManager database", message)
        self.assertIn("Cause: database rejected [password hidden]", message)
        self.assertIn("No existing database or account was changed.", message)
        self.assertNotIn("incomplete database was removed", message)
        self.assertNotIn("secret-application-password", message)


if __name__ == "__main__":
    unittest.main()
