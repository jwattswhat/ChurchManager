"""Authorized encrypted persistence for minimum-necessary pastoral notes."""

from __future__ import annotations

import base64

from pastoral_care_service import PastoralCareValidationError, _identifier
from pastoral_note_crypto import EncryptedPastoralNote, pastoral_note_binding


class PastoralRestrictedNoteConflictError(RuntimeError):
    """Raised when a restricted note changed before an update completed."""


class PastoralRestrictedNoteService:
    """Authorize note access before any encrypted row is read or written."""

    def __init__(self, repository, care_service, session, authorization):
        self.repository = repository
        self.care_service = care_service
        self.session = session
        self.authorization = authorization

    def read(self, note_id):
        """Decrypt one note after note and care-record authorization pass."""

        self.authorization.require("pastoral.notes.view", "view restricted pastoral notes")
        metadata = self.repository.metadata(_identifier(note_id, "restricted note"))
        if metadata is None:
            raise PastoralCareValidationError("The restricted pastoral note is unavailable.")
        self.care_service.need(metadata["care_need_id"])
        return self.repository.read(metadata, self.session.user_id)

    def list_for_need(self, care_need_id):
        """List note metadata only after care-record and note authorization."""

        self.authorization.require(
            "pastoral.notes.view", "list restricted pastoral notes"
        )
        care_need_id = _identifier(care_need_id, "care need")
        self.care_service.need(care_need_id)
        return self.repository.list_metadata(care_need_id)

    def create(self, care_need_id, plaintext, care_action_id=None):
        """Create a bound ciphertext row after explicit edit authorization."""

        self.authorization.require("pastoral.notes.edit", "create restricted pastoral notes")
        need = self.care_service.need(_identifier(care_need_id, "care need"))
        action_id = None if care_action_id is None else _identifier(care_action_id, "care action")
        return self.repository.create(
            need, plaintext, action_id, self.session.user_id
        )

    def update(self, note_id, plaintext, version):
        """Replace note ciphertext with optimistic concurrency protection."""

        self.authorization.require("pastoral.notes.edit", "update restricted pastoral notes")
        metadata = self.repository.metadata(_identifier(note_id, "restricted note"))
        if metadata is None:
            raise PastoralCareValidationError("The restricted pastoral note is unavailable.")
        self.care_service.need(metadata["care_need_id"])
        return self.repository.update(
            metadata, plaintext, _identifier(version, "version"), self.session.user_id
        )


class MariaDBPastoralRestrictedNoteRepository:
    """Store only ciphertext and bind it to its immutable database identity."""

    def __init__(self, connection, cipher):
        self.connection = connection
        self.cipher = cipher
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def metadata(self, note_id):
        """Return identifiers needed for authorization, never note content."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ID,ChurchID,CareNeedID,CareActionID,Version "
                "FROM tblPastoralRestrictedNote WHERE ID=?",
                (note_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return dict(zip(
                ("id", "church_id", "care_need_id", "care_action_id", "version"), row
            ))
        finally:
            cursor.close()

    def list_metadata(self, care_need_id):
        """Return display-safe note metadata without reading ciphertext."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT n.ID,n.CareActionID,n.CreatedAt,n.UpdatedAt,n.Version,"
                "COALESCE(u.DisplayName,u.Username) "
                "FROM tblPastoralRestrictedNote n "
                "JOIN tblUser u ON u.ID=n.UpdatedByUserID "
                "WHERE n.CareNeedID=? ORDER BY n.CreatedAt DESC,n.ID DESC",
                (care_need_id,),
            )
            return [dict(zip(
                ("id", "care_action_id", "created_at", "updated_at", "version", "updated_by"),
                row,
            )) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def read(self, metadata, user_id):
        """Read, audit, and decrypt one already-authorized note."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT Algorithm,KeyVersion,Nonce,Ciphertext,AuthenticationTag "
                "FROM tblPastoralRestrictedNote WHERE ID=?",
                (metadata["id"],),
            )
            row = cursor.fetchone()
            if not row:
                raise PastoralCareValidationError("The restricted pastoral note is unavailable.")
            encrypted = EncryptedPastoralNote(
                algorithm=row[0], key_version=row[1], nonce=_encode(row[2]),
                ciphertext=_encode(row[3]), authentication_tag=_encode(row[4]),
            )
            binding = self._binding(metadata)
            plaintext = self.cipher.decrypt(encrypted, binding)
            self._audit(cursor, user_id, "PASTORAL_NOTE_VIEWED", metadata["id"])
            self.connection.commit()
            return plaintext
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def create(self, need, plaintext, care_action_id, user_id):
        """Allocate an ID, bind ciphertext to it, and audit in one transaction."""

        cursor = self.connection.cursor()
        try:
            key_version = self._active_key_version(cursor)
            if care_action_id is not None:
                self._execute(
                    cursor,
                    "SELECT ID FROM tblPastoralCareAction WHERE ID=? AND CareNeedID=?",
                    (care_action_id, need["id"]),
                )
                if not cursor.fetchone():
                    raise PastoralCareValidationError(
                        "The selected pastoral action does not belong to this care record."
                    )
            self._execute(
                cursor,
                "INSERT INTO tblPastoralRestrictedNote "
                "(ChurchID,CareNeedID,CareActionID,Ciphertext,Nonce,AuthenticationTag,"
                "Algorithm,KeyVersion,CreatedByUserID,UpdatedByUserID) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (need["church_id"], need["id"], care_action_id, b"\0", b"\0" * 12,
                 b"\0" * 16, "AES-256-GCM", key_version, user_id, user_id),
            )
            note_id = cursor.lastrowid
            metadata = {
                "id": note_id, "church_id": need["church_id"],
                "care_need_id": need["id"], "care_action_id": care_action_id,
            }
            encrypted = self.cipher.encrypt(
                plaintext, self._binding(metadata), key_version=key_version
            )
            self._write_ciphertext(cursor, note_id, encrypted, user_id)
            self._audit(cursor, user_id, "PASTORAL_NOTE_CREATED", note_id)
            self.connection.commit()
            return note_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def update(self, metadata, plaintext, version, user_id):
        """Re-encrypt an authorized note and reject stale record versions."""

        cursor = self.connection.cursor()
        try:
            key_version = self._active_key_version(cursor)
            encrypted = self.cipher.encrypt(
                plaintext, self._binding(metadata), key_version=key_version
            )
            values = _encrypted_values(encrypted)
            self._execute(
                cursor,
                "UPDATE tblPastoralRestrictedNote SET Ciphertext=?,Nonce=?,"
                "AuthenticationTag=?,Algorithm=?,KeyVersion=?,UpdatedByUserID=?,"
                "Version=Version+1 WHERE ID=? AND Version=?",
                (*values, user_id, metadata["id"], version),
            )
            if cursor.rowcount != 1:
                raise PastoralRestrictedNoteConflictError(
                    "This restricted pastoral note changed. Reopen it and try again."
                )
            self._audit(cursor, user_id, "PASTORAL_NOTE_UPDATED", metadata["id"])
            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def _active_key_version(self, cursor):
        """Return the configured positive key version or fail closed."""

        self._execute(
            cursor,
            "SELECT ActiveKeyVersion,RecoveryVerified "
            "FROM tblPastoralEncryptionState WHERE ID=1",
        )
        row = cursor.fetchone()
        try:
            key_version = int(row[0]) if row else 0
        except (TypeError, ValueError):
            key_version = 0
        if key_version <= 0:
            raise PastoralCareValidationError(
                "Pastoral-note encryption is not configured."
            )
        if not bool(row[1]):
            raise PastoralCareValidationError(
                "Pastoral-note recovery has not been verified."
            )
        return key_version

    def _write_ciphertext(self, cursor, note_id, encrypted, user_id):
        values = _encrypted_values(encrypted)
        self._execute(
            cursor,
            "UPDATE tblPastoralRestrictedNote SET Ciphertext=?,Nonce=?,AuthenticationTag=?,"
            "Algorithm=?,KeyVersion=?,UpdatedByUserID=? WHERE ID=?",
            (*values, user_id, note_id),
        )

    @staticmethod
    def _binding(metadata):
        return pastoral_note_binding(
            metadata["church_id"], metadata["id"], metadata["care_need_id"],
            metadata.get("care_action_id"),
        )

    def _audit(self, cursor, user_id, action, note_id):
        self._execute(
            cursor,
            "INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID) "
            "VALUES (?,?,?,?)",
            (user_id, action, "PastoralRestrictedNote", str(note_id)),
        )


def _encode(value):
    return base64.b64encode(bytes(value)).decode("ascii")


def _encrypted_values(encrypted):
    return (
        base64.b64decode(encrypted.ciphertext), base64.b64decode(encrypted.nonce),
        base64.b64decode(encrypted.authentication_tag), encrypted.algorithm,
        encrypted.key_version,
    )
