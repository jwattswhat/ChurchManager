"""Execute a validated fresh-install plan using the guarded services.

This module contains no graphical code and never persists an administrative
credential.  The setup wizard supplies open connections and receives a
password-free result suitable for its completion page.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from baseline_installer import BaselineInstaller, load_baseline, load_seed
from database_provisioning import FreshDatabaseProvisioner, quote_identifier
from hymnal_packages import HymnalPackageImporter, load_hymnal_package
from initial_master import InitialMasterBootstrapper
from installation_plan import InstallationPlan
from lectionary_importer import LectionaryPackageImporter
from lectionary_packages import load_lectionary_package
from migration_service import MigrationService
from order_of_service_packages import (
    OrderOfServicePackageImporter,
    load_order_of_service_package,
)


ROOT = Path(__file__).resolve().parent


class InstallationExecutionError(RuntimeError):
    """Raised when a fresh installation cannot be completed safely."""


@dataclass(frozen=True)
class InstallationResult:
    """Non-secret evidence returned after a successful fresh installation."""

    database_name: str
    application_user: str
    church_id: int
    master_user_id: int
    database_objects: int
    represented_migrations: int
    active_permissions: int
    installed_packages: tuple[str, ...]


class FreshInstallationExecutor:
    """Create, populate, and verify one new local ChurchManager database.

    A failure after database creation removes the new database and account.
    Existing databases and accounts are rejected by the provisioner and are
    never adopted, repaired, or overwritten by this fresh-install service.
    """

    def __init__(
        self, admin_connection, connector, *, root=ROOT,
        database_errors=(Exception,), progress=None,
    ):
        self.admin = admin_connection
        self.connector = connector
        self.root = Path(root)
        self.database_errors = database_errors
        self.progress = progress or (lambda _message: None)

    def install(
        self, plan, application_user, application_password,
        master_password, master_confirmation,
    ):
        """Apply a validated plan and return only non-secret verification data."""
        if not isinstance(plan, InstallationPlan):
            raise InstallationExecutionError("The installation plan is invalid.")
        host = "127.0.0.1"
        provisioned = None
        connection = None
        try:
            self.progress("Creating the ChurchManager database...")
            provisioned = FreshDatabaseProvisioner(
                self.admin, database_errors=self.database_errors,
            ).create(
                plan.database_name, application_user, application_password,
                application_host=host, confirmation=plan.database_name,
            )
            connection = self.connector(
                host=host, database=plan.database_name,
                user=application_user, password=application_password,
            )
            self.progress("Installing the verified database structure...")
            baseline = self.root / "installation"
            schema, manifest = load_baseline(
                baseline / "baseline_schema.sql",
                baseline / "baseline_manifest.json",
                self.root / "migrations",
            )
            seed, _seed_manifest = load_seed(
                baseline / "baseline_seed.sql",
                baseline / "baseline_seed_manifest.json",
                self.root / "migrations",
            )
            evidence = BaselineInstaller(
                connection, database_errors=self.database_errors,
            ).install(schema, manifest, seed)
            migrations = MigrationService(
                connection, self.root / "migrations",
                database_errors=self.database_errors,
            ).run(apply=True)
            connection.commit()
            if migrations.pending != migrations.newly_applied:
                raise InstallationExecutionError(
                    "The current release migrations did not finish."
                )
            church_id = self._create_church(connection, plan.church_name)
            self.progress("Creating the Master Administrator...")
            master_id = InitialMasterBootstrapper(connection).create(
                plan.master_username, plan.master_display_name,
                master_password, master_confirmation,
                plan.master_email, plan.master_phone,
            )
            installed = self._install_packages(connection, plan, church_id)
            self._verify(connection, plan, church_id, master_id, installed)
            self.progress("Fresh installation verified.")
            return InstallationResult(
                plan.database_name, application_user, church_id, master_id,
                evidence["database_objects"],
                evidence["represented_migrations"],
                evidence["active_permissions"], tuple(installed),
            )
        except Exception as error:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass
                connection = None
            if provisioned is not None:
                self._remove_incomplete(
                    plan.database_name, application_user, host,
                )
            if isinstance(error, InstallationExecutionError):
                raise
            raise InstallationExecutionError(
                "ChurchManager could not complete the fresh installation. "
                "The incomplete database was removed."
            ) from error
        finally:
            master_password = ""
            master_confirmation = ""
            application_password = ""
            if connection is not None:
                connection.close()

    @staticmethod
    def _create_church(connection, name):
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO tblChurch (Church,City,State,Zip) VALUES (?,NULL,NULL,NULL)",
                (name,),
            )
            church_id = int(cursor.lastrowid)
            connection.commit()
            return church_id
        finally:
            cursor.close()

    def _install_packages(self, connection, plan, church_id):
        installed = []
        hymnal_codes = []
        hymnal_ids = {}
        selections = {item.code.casefold(): item for item in plan.selected_packages}
        for item in plan.selected_packages:
            if item.family != "hymnal":
                continue
            self.progress(f"Installing hymnal: {item.title}")
            package, checksum = load_hymnal_package(item.path)
            summary = HymnalPackageImporter(connection).install(package, checksum)
            hymnal_codes.append(summary.package_code)
            hymnal_ids[summary.package_code] = summary.hymnal_id
            installed.append(summary.package_code)
        if plan.primary_hymnal:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE tblChurch SET PrimaryHymnalID=? WHERE ID=?",
                    (hymnal_ids[plan.primary_hymnal], church_id),
                )
                connection.commit()
            finally:
                cursor.close()
        for item in plan.selected_packages:
            if item.family != "lectionary":
                continue
            self.progress(f"Installing lectionary: {item.title}")
            package, checksum = load_lectionary_package(item.path)
            primary_key = None
            if plan.default_lectionary == item.code.casefold():
                primary_key = self._first_edition_key(package)
            summary = LectionaryPackageImporter(connection).install(
                package, checksum, church_id if primary_key else None, primary_key,
            )
            installed.append(summary.package_code)
        for item in plan.selected_packages:
            if item.family != "order_of_service":
                continue
            self.progress(f"Installing Order of Service: {item.title}")
            package, checksum = load_order_of_service_package(item.path)
            summary = OrderOfServicePackageImporter(
                connection, hymnal_codes, hymnal_ids,
            ).install(package, checksum)
            installed.append(summary.package_code)
        return installed

    @staticmethod
    def _first_edition_key(package):
        for system in package.get("systems", []):
            for edition in system.get("editions", []):
                key = str(edition.get("edition_key") or "").strip()
                if key:
                    return key
        raise InstallationExecutionError(
            "The selected default lectionary has no edition."
        )

    @staticmethod
    def _verify(connection, plan, church_id, master_id, installed):
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM tblChurch WHERE ID=? AND Church=?",
                (church_id, plan.church_name),
            )
            church_ok = int(cursor.fetchone()[0]) == 1
            cursor.execute(
                "SELECT COUNT(*) FROM tblUser WHERE ID=? AND Active=1 "
                "AND MasterAdministrator=1 AND MustChangePassword=1",
                (master_id,),
            )
            master_ok = int(cursor.fetchone()[0]) == 1
            if not church_ok or not master_ok:
                raise InstallationExecutionError(
                    "The congregation or initial administrator did not verify."
                )
            expected = {item.code.casefold() for item in plan.selected_packages}
            if set(installed) != expected:
                raise InstallationExecutionError(
                    "The selected catalog packages did not all verify."
                )
        finally:
            cursor.close()

    def _remove_incomplete(self, database_name, application_user, host):
        cursor = self.admin.cursor()
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {quote_identifier(database_name)}")
            cursor.execute(f"DROP USER IF EXISTS '{application_user}'@'{host}'")
        except self.database_errors as cleanup_error:
            raise InstallationExecutionError(
                "Installation failed and automatic cleanup also needs attention."
            ) from cleanup_error
        finally:
            cursor.close()
