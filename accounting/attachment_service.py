"""Protected source-document storage and audited attachment metadata."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import uuid

from .draft_service import AccountingDraftError


PROHIBITED_EXTENSIONS = {
    ".bat", ".cmd", ".com", ".cpl", ".exe", ".hta", ".js", ".jse",
    ".lnk", ".msi", ".msp", ".ps1", ".reg", ".scr", ".vbs", ".vbe",
    ".wsf", ".wsh",
}


@dataclass(frozen=True)
class AttachmentPolicy:
    root: Path
    allowed_extensions: frozenset[str]
    maximum_bytes: int


def load_attachment_policy(config, test_mode=False):
    settings = config.get("attachments", {})
    key = "test_root" if test_mode else "production_root"
    raw_root = settings.get(key)
    if not raw_root:
        raise RuntimeError("The attachment storage folder is not configured.")
    root = Path(os.path.expandvars(raw_root)).expanduser().resolve()
    extensions = frozenset(
        str(item).lower() if str(item).startswith(".") else "." + str(item).lower()
        for item in settings.get("allowed_extensions", ())
    )
    maximum_mb = int(settings.get("maximum_megabytes", 20))
    if not extensions or maximum_mb < 1:
        raise RuntimeError("The attachment file policy is not configured correctly.")
    if extensions & PROHIBITED_EXTENSIONS:
        raise RuntimeError("Executable attachment types cannot be allowed.")
    return AttachmentPolicy(root, extensions, maximum_mb * 1024 * 1024)


class AttachmentStore:
    def __init__(self, policy):
        self.policy = policy

    def _safe_path(self, stored_path):
        candidate = (self.policy.root / stored_path).resolve()
        if candidate.parent != self.policy.root:
            raise AccountingDraftError("The attachment path is outside protected storage.")
        return candidate

    @staticmethod
    def _hash(path):
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def add(self, source_path):
        source = Path(source_path)
        if not source.is_file():
            raise AccountingDraftError("Select an existing attachment file.")
        extension = source.suffix.lower()
        if extension in PROHIBITED_EXTENSIONS or extension not in self.policy.allowed_extensions:
            raise AccountingDraftError("That attachment file type is not allowed.")
        size = source.stat().st_size
        if size <= 0:
            raise AccountingDraftError("The attachment file is empty.")
        if size > self.policy.maximum_bytes:
            raise AccountingDraftError("The attachment exceeds the configured size limit.")
        self.policy.root.mkdir(parents=True, exist_ok=True)
        stored_name = uuid.uuid4().hex + extension
        destination = self._safe_path(stored_name)
        temporary = self._safe_path(stored_name + ".tmp")
        try:
            shutil.copyfile(source, temporary)
            digest = self._hash(temporary)
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()
        return stored_name, source.name, digest, size

    def verify(self, stored_path, expected_hash):
        path = self._safe_path(stored_path)
        if not path.is_file():
            raise AccountingDraftError("The attachment file is missing.")
        if self._hash(path) != expected_hash:
            raise AccountingDraftError("The attachment file has changed since it was added.")
        return path

    def remove(self, stored_path):
        path = self._safe_path(stored_path)
        if path.exists():
            path.unlink()


class AccountingAttachmentService:
    def __init__(self, connection, acting_user_id, store):
        self.connection = connection
        self.acting_user_id = int(acting_user_id)
        self.store = store
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def _draft(self, cursor, transaction_id, can_edit_any=False, lock=False):
        suffix = " FOR UPDATE" if lock else ""
        self._execute(
            cursor,
            "SELECT OrganizationID,CreatedByUserID,Status FROM "
            "tblAccountingTransaction WHERE ID=?" + suffix,
            (transaction_id,),
        )
        row = cursor.fetchone()
        if row is None or row[2] != "DRAFT":
            raise AccountingDraftError("Attachments can be changed only on a saved draft.")
        if row[1] != self.acting_user_id and not can_edit_any:
            raise AccountingDraftError("You may change attachments only on drafts you can edit.")
        return row

    def list(self, transaction_id, can_edit_any=False):
        cursor = self.connection.cursor()
        try:
            self._draft(cursor, transaction_id, can_edit_any)
            self._execute(
                cursor,
                "SELECT a.ID,a.OriginalName,a.DocumentType,a.FileHash,a.StoredPath,"
                "a.AddedAt,u.DisplayName FROM tblAccountingAttachment a "
                "JOIN tblUser u ON u.ID=a.AddedByUserID "
                "WHERE a.TransactionID=? ORDER BY a.AddedAt,a.ID",
                (transaction_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def add(self, transaction_id, source_path, document_type, can_edit_any=False):
        document_type = (document_type or "Other").strip()[:100]
        stored_name = None
        cursor = self.connection.cursor()
        try:
            draft = self._draft(cursor, transaction_id, can_edit_any, lock=True)
            stored_name, original_name, digest, size = self.store.add(source_path)
            self._execute(
                cursor,
                "INSERT INTO tblAccountingAttachment "
                "(TransactionID,StoredPath,OriginalName,DocumentType,FileHash,AddedByUserID) "
                "VALUES (?,?,?,?,?,?)",
                (transaction_id, stored_name, original_name, document_type,
                 digest, self.acting_user_id),
            )
            attachment_id = cursor.lastrowid
            after = json.dumps({"original_name": original_name, "document_type": document_type,
                                "sha256": digest, "size": size}, separators=(",", ":"))
            self._execute(cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID,EntityType,EntityID,Action,AfterJSON,UserID) "
                "VALUES (?,'ATTACHMENT',?,'ATTACHMENT_ADDED',?,?)",
                (draft[0], str(attachment_id), after, self.acting_user_id))
            self.connection.commit()
            return attachment_id
        except Exception:
            self.connection.rollback()
            if stored_name:
                self.store.remove(stored_name)
            raise
        finally:
            cursor.close()

    def verify(self, transaction_id, attachment_id, can_edit_any=False):
        cursor = self.connection.cursor()
        try:
            self._draft(cursor, transaction_id, can_edit_any)
            self._execute(cursor,
                "SELECT StoredPath,FileHash FROM tblAccountingAttachment "
                "WHERE ID=? AND TransactionID=?", (attachment_id, transaction_id))
            row = cursor.fetchone()
            if row is None:
                raise AccountingDraftError("The attachment is no longer available.")
            return self.store.verify(row[0], row[1])
        finally:
            cursor.close()

    def remove(self, transaction_id, attachment_id, can_edit_any=False):
        cursor = self.connection.cursor()
        try:
            draft = self._draft(cursor, transaction_id, can_edit_any, lock=True)
            self._execute(cursor,
                "SELECT StoredPath,OriginalName,DocumentType,FileHash FROM "
                "tblAccountingAttachment WHERE ID=? AND TransactionID=? FOR UPDATE",
                (attachment_id, transaction_id))
            row = cursor.fetchone()
            if row is None:
                raise AccountingDraftError("The attachment is no longer available.")
            before = json.dumps({"original_name": row[1], "document_type": row[2],
                                 "sha256": row[3]}, separators=(",", ":"))
            self._execute(cursor, "DELETE FROM tblAccountingAttachment WHERE ID=?", (attachment_id,))
            self._execute(cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID,EntityType,EntityID,Action,BeforeJSON,UserID) "
                "VALUES (?,'ATTACHMENT',?,'ATTACHMENT_REMOVED',?,?)",
                (draft[0], str(attachment_id), before, self.acting_user_id))
            self.connection.commit()
            self.store.remove(row[0])
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
