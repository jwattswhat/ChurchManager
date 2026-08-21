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
        """Return batches that still require Giving-side action."""
        return self.all(
            "SELECT b.ID,b.BatchDate,b.Description,o.LegalName,b.ControlTotal,"
            "b.CalculatedTotal,b.Version,b.Status,b.AccountingTransactionID FROM tblContributionBatch b "
            "JOIN tblAccountingOrganization o ON o.ID=b.OrganizationID "
            "WHERE b.ChurchID=? AND (b.Status='DRAFT' OR "
            "(b.Status='READY' AND b.AccountingTransactionID IS NULL)) "
            "ORDER BY b.BatchDate DESC,b.ID DESC", (self.church_id(),),
        )

    def organizations(self):
        """Return active accounting organizations available to new batches."""
        return self.all("SELECT ID,LegalName FROM tblAccountingOrganization WHERE Active=1 ORDER BY LegalName")

    def bank_accounts(self, organization_id):
        """Return active deposit accounts for one accounting organization."""
        return self.all(
            "SELECT b.ID,CONCAT(b.Name,' - ',a.Code,' ',a.Name) FROM tblAccountingBankAccount b "
            "JOIN tblAccountingAccount a ON a.ID=b.AccountID "
            "WHERE b.OrganizationID=? AND b.Active=1 AND a.Active=1 ORDER BY b.Name,b.ID",
            (organization_id,),
        )

    def contributors(self):
        """Return active contributor identities for confidential entry."""
        return self.all("SELECT ID,DisplayName FROM tblContributionContributor "
                        "WHERE ChurchID=? AND IsActive=1 ORDER BY DisplayName,ID", (self.church_id(),))

    def purposes(self, organization_id, received_date):
        """Return approved purposes and their accounting mappings for a gift date."""
        return self.all(
            "SELECT ID,Name,OrganizationID,FundID,RevenueAccountID,FunctionID,StatementTreatment "
            "FROM tblContributionPurpose WHERE ChurchID=? AND OrganizationID=? AND IsActive=1 "
            "AND EffectiveFrom<=? AND (EffectiveThrough IS NULL OR EffectiveThrough>=?) "
            "ORDER BY Name,ID", (self.church_id(), organization_id, received_date, received_date),
        )

    def batch(self, batch_id):
        """Return one batch header scoped to this church."""
        rows = self.all("SELECT ID,BatchDate,Description,OrganizationID,ControlTotal,CalculatedTotal,"
                        "Status,Version,DepositDate,BankAccountID FROM tblContributionBatch WHERE ID=? AND ChurchID=?",
                        (batch_id, self.church_id()))
        return rows[0] if rows else None

    def contributions(self, batch_id):
        """Return gift-entry rows without notes or acknowledgment details."""
        return self.all(
            "SELECT g.ID,g.ReceivedDate,COALESCE(c.DisplayName,'Anonymous'),"
            "COALESCE(g.EnteredEnvelopeNumber,''),g.ContributionMethod,g.Amount,"
            "g.StatementEligibility FROM tblContribution g LEFT JOIN tblContributionContributor c "
            "ON c.ID=g.ContributorID JOIN tblContributionBatch b ON b.ID=g.BatchID "
            "WHERE g.BatchID=? AND b.ChurchID=? ORDER BY g.ID",
            (batch_id, self.church_id()),
        )

    def gift(self, batch_id, contribution_id):
        """Return one editable draft gift and its allocations."""
        rows = self.all(
            "SELECT g.ID,g.ContributorID,COALESCE(g.EnteredEnvelopeNumber,''),g.ContributionMethod,"
            "COALESCE(g.ReferenceValue,''),g.ReceivedDate,g.Amount,g.StatementEligibility,COALESCE(g.Note,'') "
            "FROM tblContribution g JOIN tblContributionBatch b ON b.ID=g.BatchID "
            "WHERE g.ID=? AND g.BatchID=? AND b.ChurchID=? AND b.Status='DRAFT'",
            (contribution_id, batch_id, self.church_id()))
        if not rows: return None
        allocations = self.all(
            "SELECT a.PurposeID,a.OrganizationID,a.FundID,a.RevenueAccountID,a.FunctionID,a.Amount,"
            "COALESCE(a.DonorRestrictionNote,''),p.Name FROM tblContributionAllocation a "
            "LEFT JOIN tblContributionPurpose p ON p.ID=a.PurposeID WHERE a.ContributionID=? ORDER BY a.ID",
            (contribution_id,))
        return rows[0], allocations

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
        gift_amount = validate_allocations(amount, [item[5] for item in allocations])
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
            for purpose_id, allocation_org, fund_id, account_id, function_id, allocation_amount, restriction in allocations:
                cursor.execute(
                    "INSERT INTO tblContributionAllocation "
                    "(ContributionID,PurposeID,OrganizationID,FundID,RevenueAccountID,FunctionID,Amount,DonorRestrictionNote) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (contribution_id, purpose_id, allocation_org, fund_id, account_id, function_id,
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

    def update_monetary_gift(self, contribution_id, **values):
        """Replace an editable gift and its allocations while retaining its identity."""
        batch_id = values["batch_id"]; received_date = values["received_date"]
        allocations = list(values["allocations"])
        amount = validate_allocations(values["amount"], [item[5] for item in allocations])
        method = str(values.get("method") or "").upper()
        if method not in {"CASH", "CHECK", "ELECTRONIC", "OTHER"}:
            raise GivingValidationError("Select a valid monetary contribution method.")
        eligibility = str(values.get("statement_eligibility") or "").upper()
        if eligibility not in {"ELIGIBLE", "INELIGIBLE", "REVIEW"}:
            raise GivingValidationError("Select a valid statement treatment.")
        envelope = str(values.get("envelope_number") or "").strip() or None
        contributor_id = values.get("contributor_id")
        if contributor_id is None and envelope: contributor_id = self.resolve_envelope(envelope, received_date)
        church_id = self.church_id(); cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT OrganizationID,Status FROM tblContributionBatch "
                           "WHERE ID=? AND ChurchID=? FOR UPDATE", (batch_id, church_id))
            batch = cursor.fetchone()
            if not batch or batch[1] != "DRAFT":
                raise GivingValidationError("Only a draft contribution can be changed.")
            if any(item[1] != batch[0] for item in allocations):
                raise GivingValidationError("Every allocation must use the batch organization.")
            cursor.execute("UPDATE tblContribution SET ContributorID=?,EnteredEnvelopeNumber=?,"
                           "ContributionMethod=?,ReferenceValue=?,ReceivedDate=?,Amount=?,StatementEligibility=?,Note=? "
                           "WHERE ID=? AND BatchID=?",
                           (contributor_id, envelope, method, values.get("reference") or None,
                            received_date, amount, eligibility, values.get("note") or None,
                            contribution_id, batch_id))
            if cursor.rowcount != 1: raise GivingValidationError("The selected contribution is unavailable.")
            cursor.execute("DELETE FROM tblContributionAllocation WHERE ContributionID=?", (contribution_id,))
            self._insert_allocations(cursor, contribution_id, allocations)
            self._refresh_total(cursor, batch_id)
            self._audit(cursor, church_id, "CONTRIBUTION_UPDATED", "BATCH", batch_id,
                        f"Draft batch {batch_id}")
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def delete_gift(self, batch_id, contribution_id):
        """Delete one draft gift, refresh totals, and retain a safe audit event."""
        church_id = self.church_id(); cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT Status FROM tblContributionBatch WHERE ID=? AND ChurchID=? FOR UPDATE",
                           (batch_id, church_id)); row = cursor.fetchone()
            if not row or row[0] != "DRAFT": raise GivingValidationError("Only a draft contribution can be deleted.")
            cursor.execute("DELETE FROM tblContributionAllocation WHERE ContributionID=?", (contribution_id,))
            cursor.execute("DELETE FROM tblContribution WHERE ID=? AND BatchID=?", (contribution_id, batch_id))
            if cursor.rowcount != 1: raise GivingValidationError("The selected contribution is unavailable.")
            self._refresh_total(cursor, batch_id)
            self._audit(cursor, church_id, "CONTRIBUTION_DELETED", "BATCH", batch_id,
                        f"Draft batch {batch_id}")
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def review_issues(self, batch_id):
        """Return privacy-safe reasons a draft batch cannot yet be marked ready."""
        cursor = self.connection.cursor()
        try:
            return self._review_issues(cursor, batch_id, self.church_id())
        finally:
            cursor.close()

    def mark_ready(self, batch_id):
        """Atomically validate and move a complete draft batch to Ready."""
        church_id = self.church_id(); cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT Status FROM tblContributionBatch WHERE ID=? AND ChurchID=? FOR UPDATE",
                           (batch_id, church_id))
            row = cursor.fetchone()
            if not row: raise GivingValidationError("The selected contribution batch is unavailable.")
            if row[0] != "DRAFT": raise GivingValidationError("Only a draft batch can be marked ready.")
            issues = self._review_issues(cursor, batch_id, church_id)
            if issues: raise GivingValidationError("The batch is not ready:\n- " + "\n- ".join(issues))
            cursor.execute("UPDATE tblContributionBatch SET Status='READY',ReviewedByUserID=?,"
                           "ReviewedAt=CURRENT_TIMESTAMP(6),Version=Version+1 WHERE ID=? AND Status='DRAFT'",
                           (self.user_id, batch_id))
            self._audit(cursor, church_id, "BATCH_MARKED_READY", "BATCH", batch_id,
                        f"Ready batch {batch_id}")
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def _review_issues(self, cursor, batch_id, church_id):
        cursor.execute("SELECT ControlTotal,CalculatedTotal,DepositDate,BankAccountID FROM tblContributionBatch "
                       "WHERE ID=? AND ChurchID=?", (batch_id, church_id))
        batch = cursor.fetchone()
        if not batch: return ["The batch is unavailable."]
        issues = []
        if batch[1] <= 0: issues.append("Enter at least one monetary contribution.")
        if batch[0] is not None and batch[0] != batch[1]: issues.append("The entered total does not equal the control total.")
        if batch[2] is None: issues.append("Enter the bank deposit date.")
        if batch[3] is None: issues.append("Select the bank account receiving the deposit.")
        checks = (
            ("SELECT COUNT(*) FROM tblContribution WHERE BatchID=? AND EnteredEnvelopeNumber IS NOT NULL "
             "AND EnteredEnvelopeNumber<>'' AND ContributorID IS NULL",
             "Resolve or deliberately clear every unknown envelope number."),
            ("SELECT COUNT(*) FROM tblContribution WHERE BatchID=? AND DirectionStatus='REVIEW'",
             "Resolve every donor-direction review."),
            ("SELECT COUNT(*) FROM (SELECT g.ID,g.Amount,COALESCE(SUM(a.Amount),0) Allocated "
             "FROM tblContribution g LEFT JOIN tblContributionAllocation a ON a.ContributionID=g.ID "
             "WHERE g.BatchID=? GROUP BY g.ID,g.Amount HAVING Allocated<>g.Amount) invalid",
             "Every contribution must be allocated exactly."),
            ("SELECT COUNT(*) FROM tblContributionAllocation a JOIN tblContribution g ON g.ID=a.ContributionID "
             "LEFT JOIN tblContributionPurpose p ON p.ID=a.PurposeID "
             "LEFT JOIN tblAccountingFund f ON f.ID=a.FundID LEFT JOIN tblAccountingAccount ac ON ac.ID=a.RevenueAccountID "
             "LEFT JOIN tblAccountingFunction fn ON fn.ID=a.FunctionID "
             "WHERE g.BatchID=? AND (p.ID IS NULL OR p.IsActive=0 OR p.ControlAndDiscretionConfirmed=0 "
             "OR p.EffectiveFrom>g.ReceivedDate OR (p.EffectiveThrough IS NOT NULL AND p.EffectiveThrough<g.ReceivedDate) "
             "OR f.Active=0 OR f.OrganizationID<>a.OrganizationID "
             "OR ac.Active=0 OR ac.OrganizationID<>a.OrganizationID OR ac.PostingAllowed=0 OR ac.AccountType<>'REVENUE' "
             "OR (ac.FunctionRequirement='REQUIRED' AND a.FunctionID IS NULL) "
             "OR (ac.FunctionRequirement='PROHIBITED' AND a.FunctionID IS NOT NULL) "
             "OR (a.FunctionID IS NOT NULL AND (fn.ID IS NULL OR fn.Active=0 OR fn.OrganizationID<>a.OrganizationID)))",
             "Every allocation must use an effective approved purpose and active accounting destination."),
            ("SELECT COUNT(*) FROM tblContributionBatch b LEFT JOIN tblAccountingBankAccount ba ON ba.ID=b.BankAccountID "
             "WHERE b.ID=? AND (ba.ID IS NULL OR ba.Active=0 OR ba.OrganizationID<>b.OrganizationID)",
             "Select an active bank account belonging to the batch organization."),
            ("SELECT COUNT(*) FROM (SELECT ContributionMethod,ReferenceValue,COUNT(*) Uses FROM tblContribution "
             "WHERE BatchID=? AND ReferenceValue IS NOT NULL AND ReferenceValue<>'' "
             "GROUP BY ContributionMethod,ReferenceValue HAVING Uses>1) duplicate_reference",
             "Resolve duplicate check or reference values."),
        )
        for sql, message in checks:
            cursor.execute(sql, (batch_id,))
            if cursor.fetchone()[0]: issues.append(message)
        return issues

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

    @staticmethod
    def _insert_allocations(cursor, contribution_id, allocations):
        for purpose_id, organization_id, fund_id, account_id, function_id, amount, restriction in allocations:
            cursor.execute("INSERT INTO tblContributionAllocation "
                           "(ContributionID,PurposeID,OrganizationID,FundID,RevenueAccountID,FunctionID,Amount,DonorRestrictionNote) "
                           "VALUES (?,?,?,?,?,?,?,?)",
                           (contribution_id, purpose_id, organization_id, fund_id, account_id, function_id,
                            Decimal(str(amount)).quantize(Decimal("0.01")), restriction or None))

    @staticmethod
    def _refresh_total(cursor, batch_id):
        cursor.execute("UPDATE tblContributionBatch SET CalculatedTotal=(SELECT COALESCE(SUM(Amount),0) "
                       "FROM tblContribution WHERE BatchID=?),Version=Version+1 WHERE ID=?", (batch_id, batch_id))
