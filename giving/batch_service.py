"""Transactional draft-batch persistence for confidential member giving."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from bulletin_orders import portable_connection
from giving.validation import GivingValidationError, validate_allocations


class DraftBatchService:
    """Create and edit giving batches while they remain in draft status."""

    def __init__(self, connection, user_id: int):
        self.connection = portable_connection(connection)
        self.user_id = int(user_id)

    def all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def church_id(self):
        rows = self.all("SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
        if not rows:
            raise GivingValidationError("Church information must be created first.")
        return rows[0][0]

    def draft_batches(self):
        """Return current draft batches without exposing contributor detail."""
        return self.all(
            "SELECT b.ID,b.BatchDate,b.Description,o.LegalName,b.ControlTotal,"
            "b.CalculatedTotal,b.Version FROM tblContributionBatch b "
            "JOIN tblAccountingOrganization o ON o.ID=b.OrganizationID "
            "WHERE b.ChurchID=? AND b.Status='DRAFT' "
            "ORDER BY b.BatchDate DESC,b.ID DESC", (self.church_id(),),
        )

    def create_batch(self, *, batch_date: date, description: str, organization_id: int,
                     control_total=None, service_id=None, attendance_event_id=None,
                     deposit_date=None, bank_account_id=None):
        """Create an empty draft batch and write a privacy-safe audit event."""
        description = str(description or "").strip()
        if not description:
            raise GivingValidationError("Batch description is required.")
        control = self._optional_money(control_total, "Control total")
        if control is not None and control < 0:
            raise GivingValidationError("Control total cannot be negative.")
        church_id = self.church_id()
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO tblContributionBatch "
                "(ChurchID,BatchDate,Description,ServiceID,AttendanceEventID,DepositDate,"
                "OrganizationID,BankAccountID,Status,ControlTotal,CalculatedTotal,EnteredByUserID) "
                "VALUES (?,?,?,?,?,?,?,?, 'DRAFT',?,0.00,?)",
                (church_id, batch_date, description, service_id, attendance_event_id,
                 deposit_date, organization_id, bank_account_id, control, self.user_id),
            )
            batch_id = cursor.lastrowid
            self._audit(cursor, church_id, "BATCH_CREATED", "BATCH", batch_id,
                        f"Draft batch {batch_id}")
            self.connection.commit()
            return batch_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def resolve_envelope(self, envelope_number: str, received_date: date):
        """Resolve a dated envelope assignment, returning its contributor ID or None."""
        number = str(envelope_number or "").strip()
        if not number:
            return None
        if number.isdecimal():
            predicate = "e.EnvelopeNumber REGEXP '^[0-9]+$' AND CAST(e.EnvelopeNumber AS UNSIGNED)=?"
            identity = int(number)
        else:
            predicate = "e.EnvelopeNumber=?"
            identity = number
        rows = self.all(
            "SELECT e.ContributorID FROM tblContributionEnvelopeAssignment e "
            "JOIN tblContributionContributor c ON c.ID=e.ContributorID "
            "WHERE e.ChurchID=? AND " + predicate +
            " AND e.EffectiveFrom<=? AND (e.EffectiveThrough IS NULL OR e.EffectiveThrough>=?) "
            "AND c.IsActive=1 ORDER BY e.EffectiveFrom DESC,e.ID DESC LIMIT 2",
            (self.church_id(), identity, received_date, received_date),
        )
        if len(rows) > 1:
            raise GivingValidationError("That envelope number has overlapping assignments.")
        return rows[0][0] if rows else None

    def save_monetary_gift(self, *, batch_id: int, received_date: date, amount, allocations,
                           contributor_id=None, envelope_number=None, method="CASH",
                           reference=None, statement_eligibility="ELIGIBLE", note=None):
        """Add one monetary gift and balanced allocations to an editable batch."""
        allocations = list(allocations)
        gift_amount = validate_allocations(amount, [item[4] for item in allocations])
        method = str(method or "").upper()
        if method not in {"CASH", "CHECK", "ELECTRONIC", "OTHER"}:
            raise GivingValidationError("Select a valid monetary contribution method.")
        eligibility = str(statement_eligibility or "").upper()
        if eligibility not in {"ELIGIBLE", "INELIGIBLE", "REVIEW"}:
            raise GivingValidationError("Select a valid statement treatment.")
        entered_envelope = str(envelope_number or "").strip() or None
        if contributor_id is None and entered_envelope:
            contributor_id = self.resolve_envelope(entered_envelope, received_date)
        church_id = self.church_id()
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT OrganizationID,Status FROM tblContributionBatch "
                           "WHERE ID=? AND ChurchID=? FOR UPDATE", (batch_id, church_id))
            batch = cursor.fetchone()
            if not batch:
                raise GivingValidationError("The selected contribution batch is unavailable.")
            if batch[1] != "DRAFT":
                raise GivingValidationError("Only a draft contribution batch can be changed.")
            organization_id = batch[0]
            if any(item[1] != organization_id for item in allocations):
                raise GivingValidationError("Every allocation must use the batch organization.")
            cursor.execute(
                "INSERT INTO tblContribution "
                "(BatchID,ContributorID,EnteredEnvelopeNumber,ContributionMethod,ReferenceValue,"
                "ReceivedDate,Amount,StatementEligibility,Note) VALUES (?,?,?,?,?,?,?,?,?)",
                (batch_id, contributor_id, entered_envelope, method, reference or None,
                 received_date, gift_amount, eligibility, note or None),
            )
            contribution_id = cursor.lastrowid
            for purpose_id, allocation_org, fund_id, account_id, allocation_amount, restriction in allocations:
                cursor.execute(
                    "INSERT INTO tblContributionAllocation "
                    "(ContributionID,PurposeID,OrganizationID,FundID,RevenueAccountID,Amount,DonorRestrictionNote) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (contribution_id, purpose_id, allocation_org, fund_id, account_id,
                     Decimal(str(allocation_amount)).quantize(Decimal("0.01")), restriction or None),
                )
            cursor.execute("UPDATE tblContributionBatch SET CalculatedTotal=(SELECT COALESCE(SUM(Amount),0) "
                           "FROM tblContribution WHERE BatchID=?),Version=Version+1 WHERE ID=?",
                           (batch_id, batch_id))
            self._audit(cursor, church_id, "CONTRIBUTION_ADDED", "BATCH", batch_id,
                        f"Draft batch {batch_id}")
            self.connection.commit()
            return contribution_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    @staticmethod
    def _optional_money(value, label):
        if value in (None, ""):
            return None
        try:
            amount = Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError, ValueError) as error:
            raise GivingValidationError(f"{label} must be a valid monetary amount.") from error
        if not amount.is_finite():
            raise GivingValidationError(f"{label} must be a finite monetary amount.")
        return amount

    def _audit(self, cursor, church_id, action, entity_type, entity_id, safe_reference):
        cursor.execute("INSERT INTO tblContributionAuditEvent "
                       "(ChurchID,UserID,Action,EntityType,EntityID,SafeReference) VALUES (?,?,?,?,?,?)",
                       (church_id, self.user_id, action, entity_type, entity_id, safe_reference))
