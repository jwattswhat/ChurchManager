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

        return (
            self.recovery.key_manager.has_key()
            and self.recovery.protected_package_path.is_file()
        )

    def configure(self, recovery_password):
        """Create missing key material and refresh its password-protected package."""

        self.authorization.require(
            self.PERMISSION, "administer pastoral-note recovery"
        )
        replaced = self.recovery.protected_package_path.is_file()
        if not self.recovery.key_manager.has_key():
            self.recovery.key_manager.provision()
        path = self.recovery.create_protected_package(recovery_password)
        self._audit(
            "PASTORAL_RECOVERY_PASSWORD_REPLACED"
            if replaced else "PASTORAL_RECOVERY_CONFIGURED"
        )
        return path

    def _audit(self, action):
        cursor = self.connection.cursor()
        try:
            sql = (
                "INSERT INTO tblSecurityAuditEvent "
                "(UserID, Action, EntityType, EntityID, Workstation) "
                "VALUES (?, ?, 'PastoralEncryptionKey', 'v1', ?)"
            ).replace("?", self.marker)
            cursor.execute(
                sql,
                (
                    self.session.user_id,
                    action,
                    self.session.workstation,
                ),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
