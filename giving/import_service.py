"""Atomic draft-batch creation from an accepted contribution import preview."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
import json

from accounting.attachment_service import AttachmentStore, load_attachment_policy
from bulletin_orders import portable_connection
from churchmanager_mode import load_config
from giving.import_parser import file_hash
from giving.validation import (
    GivingValidationError,
    require_giving_bank_account,
    require_giving_contributor,
    require_giving_organization,
)


class ContributionImportService:
    """Preserve source evidence and import accepted rows into one Draft batch."""

    def __init__(self, connection, user_id: int, authorization, test_mode=False, store=None):
        self.connection = portable_connection(connection); self.user_id = int(user_id)
        self.authorization = authorization
        self.store = store or AttachmentStore(load_attachment_policy(load_config(), test_mode))

    def import_draft(self, *, source_path, content, mapping, preview_rows, church_id,
                     organization_id, bank_account_id, deposit_date, description):
        """Create an evidence record, Draft batch, gifts, and allocations atomically."""
        self.authorization.require("giving.batches.enter", "import contribution batches")
        preview_rows = tuple(preview_rows)
        if not preview_rows or any(not item.ready for item in preview_rows):
            raise GivingValidationError("Every contribution row must be Ready before import.")
        description = str(description or "").strip()
        if not description:
            raise GivingValidationError("Enter a description for the imported draft batch.")
        digest = file_hash(content)
        total = sum((item.source.amount for item in preview_rows), Decimal("0.00"))
        stored_path = None; cursor = self.connection.cursor()
        try:
            require_giving_organization(cursor, church_id, organization_id)
            require_giving_bank_account(cursor, organization_id, bank_account_id)
            cursor.execute("SELECT ID FROM tblContributionImportEvidence WHERE ChurchID=? AND FileHash=?",
                           (church_id, digest))
            if cursor.fetchone() is not None:
                raise GivingValidationError("This contribution file has already been imported.")
            stored_path, original_name, stored_hash, size = self.store.add(source_path)
            if stored_hash != digest:
                raise GivingValidationError("The protected source copy does not match the previewed file.")
            batch_date = max(item.source.received_date for item in preview_rows)
            cursor.execute(
                "INSERT INTO tblContributionBatch "
                "(ChurchID,BatchDate,Description,DepositDate,OrganizationID,BankAccountID,Status,"
                "ControlTotal,CalculatedTotal,EnteredByUserID) VALUES (?,?,?,?,?,?,'DRAFT',?,?,?)",
                (church_id, batch_date, description[:255], deposit_date, organization_id,
                 bank_account_id, total, total, self.user_id),
            )
            batch_id = cursor.lastrowid
            for item in preview_rows:
                source = item.source
                require_giving_contributor(cursor, church_id, item.contributor_id)
                cursor.execute(
                    "SELECT OrganizationID,FundID,RevenueAccountID,FunctionID,StatementTreatment "
                    "FROM tblContributionPurpose WHERE ID=? AND ChurchID=? AND OrganizationID=? "
                    "AND IsActive=1 AND EffectiveFrom<=? AND (EffectiveThrough IS NULL OR EffectiveThrough>=?)",
                    (item.purpose_id, church_id, organization_id,
                     source.received_date, source.received_date),
                )
                purpose = cursor.fetchone()
                if purpose is None:
                    raise GivingValidationError(f"Row {source.row_number} purpose changed after preview.")
                cursor.execute(
                    "INSERT INTO tblContribution "
                    "(BatchID,ContributorID,EnteredEnvelopeNumber,ContributionMethod,ReferenceValue,"
                    "ReceivedDate,Amount,StatementEligibility,Note,DirectionStatus) "
                    "VALUES (?,?,?,?,?,?,?,?,?,'ACCEPTED')",
                    (batch_id, item.contributor_id, source.envelope_number or None, source.method,
                     source.reference or None, source.received_date, source.amount, purpose[4],
                     source.description or None),
                )
                contribution_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO tblContributionAllocation "
                    "(ContributionID,PurposeID,OrganizationID,FundID,RevenueAccountID,FunctionID,Amount) "
                    "VALUES (?,?,?,?,?,?,?)", (contribution_id, item.purpose_id, *purpose[:4], source.amount),
                )
            cursor.execute(
                "INSERT INTO tblContributionImportEvidence "
                "(ChurchID,BatchID,StoredPath,OriginalName,FileHash,FileSize,MappingJSON,RowCount,"
                "ImportedTotal,ImportedByUserID) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (church_id, batch_id, stored_path, original_name, digest, size,
                 json.dumps(asdict(mapping), separators=(",", ":")), len(preview_rows), total, self.user_id),
            )
            cursor.execute(
                "INSERT INTO tblContributionAuditEvent "
                "(ChurchID,UserID,Action,EntityType,EntityID,SafeReference) "
                "VALUES (?,?,'CONTRIBUTION_FILE_IMPORTED','BATCH',?,?)",
                (church_id, self.user_id, batch_id,
                 f"{len(preview_rows)} rows; total {total}; hash {digest[:12]}"),
            )
            self.connection.commit(); return batch_id
        except Exception:
            self.connection.rollback()
            if stored_path:
                try: self.store.remove(stored_path)
                except Exception: pass
            raise
        finally:
            cursor.close()
