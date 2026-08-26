"""Authorized setup and safe auditing for pastoral-note key recovery."""

from __future__ import annotations


class PastoralRecoveryAdministration:
    """Provision pastoral encryption recovery without retaining its password."""

    PERMISSION = "pastoral.care.admin"

    def __init__(self, connection, session, authorization, recovery):
        self.connection = connection
        self.session = session
        self.authorization = authorization
        self.recovery = recovery
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    @property
    def configured(self):
        """Return whether both the protected key and reusable package exist."""

        key_version, recovery_verified = self._active_state()
        return (
            recovery_verified
            and self.recovery.key_manager.has_key(key_version)
            and self.recovery.protected_package_path.is_file()
        )

    def configure(self, recovery_password):
        """Create missing key material and refresh its password-protected package."""

        self.authorization.require(
            self.PERMISSION, "administer pastoral-note recovery"
        )
        key_version, _recovery_verified = self._active_state()
        replaced = self.recovery.protected_package_path.is_file()
        if not self.recovery.key_manager.has_key(key_version):
            self.recovery.key_manager.provision(key_version)
        path = self.recovery.create_protected_package(
            recovery_password, key_version=key_version
        )
        self._mark_verified_and_audit(
            "PASTORAL_RECOVERY_PASSWORD_REPLACED"
            if replaced else "PASTORAL_RECOVERY_CONFIGURED",
            key_version,
        )
        return path

    def _active_state(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ActiveKeyVersion,RecoveryVerified "
                "FROM tblPastoralEncryptionState WHERE ID=1"
            )
            row = cursor.fetchone()
            if not row or int(row[0]) <= 0:
                raise RuntimeError("Pastoral-note encryption is not configured.")
            return int(row[0]), bool(row[1])
        finally:
            cursor.close()

    def _mark_verified_and_audit(self, action, key_version):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                (
                    "UPDATE tblPastoralEncryptionState SET RecoveryVerified=1 "
                    "WHERE ID=1 AND ActiveKeyVersion=?"
                ).replace("?", self.marker),
                (key_version,),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Pastoral-note recovery could not be marked verified."
                )
            sql = (
                "INSERT INTO tblSecurityAuditEvent "
                "(UserID, Action, EntityType, EntityID, Workstation) "
                "VALUES (?, ?, 'PastoralEncryptionKey', ?, ?)"
            ).replace("?", self.marker)
            cursor.execute(
                sql,
                (
                    self.session.user_id,
                    action,
                    "v{}".format(key_version),
                    self.session.workstation,
                ),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
