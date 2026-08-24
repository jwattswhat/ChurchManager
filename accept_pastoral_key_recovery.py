"""Prove pastoral ciphertext rotation and backup recovery in disposable resources."""

from __future__ import annotations

import argparse
import base64
import getpass
import secrets
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import mariadb

from accept_setup_services import plan_for, remove_disposable
from backup_service import BackupService
from installation_executor import FreshInstallationExecutor
from installation_readiness import find_mariadb_tool, inspect_readiness
from pastoral_key_rotation import MariaDBPastoralKeyRotationRepository, PastoralKeyRotationService
from pastoral_note_crypto import (
    EncryptedPastoralNote, PastoralKeyManager, PastoralNoteCipher,
    PastoralNoteCryptoError, PastoralRecoveryBackup, pastoral_note_binding,
)
from pastoral_restricted_notes import MariaDBPastoralRestrictedNoteRepository


ROOT = Path(__file__).resolve().parent
NOTE_TEXT = "Fictional recovery acceptance note."
RECOVERY_PASSWORD = "Acceptance-only pastoral recovery password"
KEY_TARGET = "ChurchManager/Acceptance/PastoralNotes"


class MemoryCredentialStore:
    """Provide isolated key storage that disappears when the rehearsal exits."""

    def __init__(self): self.values = {}
    def exists(self, target): return target in self.values
    def read(self, target): return self.values[target]
    def write(self, target, username, password): self.values[target] = (username, password)


class Authorization:
    """Grant only the administrative operation exercised by this rehearsal."""

    @staticmethod
    def require(permission, _operation):
        if permission != "pastoral.care.admin": raise PermissionError(permission)


def acceptance_names(now=None):
    """Return unique disposable database and account names."""

    stamp = (now or datetime.now()).strftime("%Y%m%d%H%M%S")
    return f"CMPastoralAcceptance_{stamp}", f"cm_pastoral_{stamp}"


def first_ids(connection):
    """Return the seeded church and Master Administrator identifiers."""

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
        church_id = int(cursor.fetchone()[0])
        cursor.execute("SELECT ID FROM tblUser ORDER BY ID LIMIT 1")
        return church_id, int(cursor.fetchone()[0])
    finally: cursor.close()


def create_fixture(connection, cipher):
    """Create one fictional care record and one encrypted restricted note."""

    church_id, user_id = first_ids(connection)
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE tblPastoralEncryptionState SET ActiveKeyVersion=1,RecoveryVerified=1 WHERE ID=1"
        )
        cursor.execute(
            "INSERT INTO tblPastoralCareNeed "
            "(ChurchID,DisplaySubject,Category,Source,Priority,Status,OpenedDate,"
            "SafeSummary,CreatedByUserID,UpdatedByUserID) VALUES "
            "(?,'Acceptance Fixture','Other','MANUAL','NORMAL','OPEN',CURRENT_DATE,"
            "'Fictional acceptance record.',?,?)",
            (church_id, user_id, user_id),
        )
        need_id = int(cursor.lastrowid)
        connection.commit()
    except Exception:
        connection.rollback(); raise
    finally: cursor.close()
    note_id = MariaDBPastoralRestrictedNoteRepository(connection, cipher).create(
        {"id": need_id, "church_id": church_id}, NOTE_TEXT, None, user_id
    )
    return user_id, note_id


def encrypted_note(connection, note_id):
    """Return encrypted fields and immutable binding identifiers."""

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT ID,ChurchID,CareNeedID,CareActionID,Algorithm,KeyVersion,"
            "Nonce,Ciphertext,AuthenticationTag FROM tblPastoralRestrictedNote WHERE ID=?",
            (note_id,),
        )
        row = cursor.fetchone()
        if row is None: raise RuntimeError("The acceptance ciphertext is missing.")
        metadata = {"id": row[0], "church_id": row[1], "care_need_id": row[2], "care_action_id": row[3]}
        encoded = lambda value: base64.b64encode(bytes(value)).decode("ascii")
        return metadata, EncryptedPastoralNote(
            row[4], row[5], encoded(row[6]), encoded(row[7]), encoded(row[8])
        )
    finally: cursor.close()


def verify_note(connection, key_manager, note_id, expected_version):
    """Prove restored ciphertext authenticates under the expected key."""

    metadata, encrypted = encrypted_note(connection, note_id)
    if int(encrypted.key_version) != int(expected_version):
        raise RuntimeError("The restored note has the wrong key version.")
    binding = pastoral_note_binding(
        metadata["church_id"], metadata["id"], metadata["care_need_id"], metadata["care_action_id"]
    )
    if PastoralNoteCipher(key_manager).decrypt(encrypted, binding) != NOTE_TEXT:
        raise RuntimeError("The restored fictional note did not decrypt correctly.")


def recovered_manager(backup, password, package_path):
    """Restore one sidecar into a fresh isolated credential store."""

    manager = PastoralKeyManager(MemoryCredentialStore(), KEY_TARGET)
    recovery = PastoralRecoveryBackup(manager, package_path)
    validated = recovery.validate_restore(backup, password)
    if validated is None: raise RuntimeError("The acceptance backup has no recovery sidecar.")
    recovery.complete_restore(validated)
    return manager, recovery


def accept(admin_password, *, keep=False, notify=print):
    """Run the complete rotation and two-checkpoint recovery proof."""

    readiness = inspect_readiness(ROOT)
    database_name, account_name = acceptance_names()
    plan = plan_for(database_name, readiness)
    application_password, master_password = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
    work = ROOT / "tmp" / "pastoral-recovery-acceptance"
    backups, safety = work / "backups", work / "safety"
    tools = find_mariadb_tool("mariadb-dump.exe").parent
    admin = application = installation = None
    succeeded = False
    try:
        admin = mariadb.connect(host="127.0.0.1", port=3306, user="root", password=admin_password, autocommit=True)
        installation = FreshInstallationExecutor(
            admin, mariadb.connect, root=ROOT, database_errors=(mariadb.Error,), progress=notify,
        ).install(
            plan, account_name, application_password, master_password, master_password,
            dump_directory=tools, backup_folder=backups,
        )
        settings = {"server": "127.0.0.1", "port": 3306, "database": database_name,
                    "user": account_name, "password": application_password}
        connect = lambda: mariadb.connect(host="127.0.0.1", port=3306, database=database_name,
                                          user=account_name, password=application_password)
        application = connect()
        manager = PastoralKeyManager(MemoryCredentialStore(), KEY_TARGET)
        manager.provision(1)
        cipher = PastoralNoteCipher(manager)
        recovery = PastoralRecoveryBackup(manager, work / "active-recovery.json")
        recovery.create_protected_package(RECOVERY_PASSWORD, key_version=1)
        user_id, note_id = create_fixture(application, cipher)
        verify_note(application, manager, note_id, 1)
        backup_service = BackupService(recovery=recovery)

        def make_backup(label):
            return backup_service.create(settings, tools, backups / label)

        rotation = PastoralKeyRotationService(
            MariaDBPastoralKeyRotationRepository(application), manager, cipher, recovery,
            SimpleNamespace(user_id=user_id, workstation="ACCEPTANCE"), Authorization(),
            lambda: make_backup("BeforeRotation"), lambda: make_backup("AfterRotation"),
        ).rotate(RECOVERY_PASSWORD)
        verify_note(application, manager, note_id, 2)
        before, after = rotation.pre_rotation_backup.path, rotation.verification_backup.path

        try: recovery.validate_restore(before, "incorrect recovery password")
        except PastoralNoteCryptoError: notify("verified wrong recovery password fails closed")
        else: raise RuntimeError("An incorrect recovery password was accepted.")

        sidecar = recovery.sidecar_path(after)
        valid_package = sidecar.read_bytes()
        sidecar.write_bytes(valid_package[:-1] + b"!")
        try: recovery.validate_restore(after, RECOVERY_PASSWORD)
        except PastoralNoteCryptoError: notify("verified tampered recovery package fails closed")
        else: raise RuntimeError("A tampered recovery package was accepted.")
        sidecar.write_bytes(valid_package)

        application.close(); application = None
        before_manager, before_recovery = recovered_manager(before, RECOVERY_PASSWORD, work / "restored-before.json")
        BackupService(recovery=before_recovery).restore(settings, tools, before, safety, recovery_password=RECOVERY_PASSWORD)
        application = connect(); verify_note(application, before_manager, note_id, 1)
        notify("verified pre-rotation backup and v1 ciphertext recovery")

        application.close(); application = None
        after_manager, after_recovery = recovered_manager(after, RECOVERY_PASSWORD, work / "restored-after.json")
        BackupService(recovery=after_recovery).restore(settings, tools, after, safety, recovery_password=RECOVERY_PASSWORD)
        application = connect(); verify_note(application, after_manager, note_id, 2)
        notify("verified post-rotation backup and v2 ciphertext recovery")
        notify("isolated_pastoral_key_recovery_accepted=true")
        succeeded = True
    finally:
        application_password = master_password = ""
        if application is not None: application.close()
        if admin is not None:
            if not keep or not succeeded:
                remove_disposable(admin, database_name, account_name)
                notify(f"removed isolated database {database_name}")
            admin.close()
        if not keep:
            if installation is not None: Path(installation.backup_path).unlink(missing_ok=True)
            for pattern in ("*.SQL", "*.json"):
                for path in work.rglob(pattern) if work.exists() else (): path.unlink(missing_ok=True)
            notify("removed isolated pastoral recovery artifacts")


def main(argv=None):
    """Preview by default; apply only after explicit local authorization."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)
    database_name, account_name = acceptance_names()
    print("pastoral_key_recovery_rehearsal=true")
    print(f"temporary_database_pattern={database_name}")
    print(f"temporary_account_pattern={account_name}")
    print("fixture=fictional_ciphertext_only")
    if not args.apply:
        print("preview_only=true"); return 0
    password = getpass.getpass("Local MariaDB administrative password for root: ")
    try: accept(password, keep=args.keep); return 0
    finally: password = ""


if __name__ == "__main__": raise SystemExit(main())
