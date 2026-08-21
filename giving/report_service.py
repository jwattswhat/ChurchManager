"""Permission-neutral read models for confidential Giving reports."""

from __future__ import annotations

from datetime import date

from bulletin_orders import portable_connection


class GivingReportService:
    """Read summary and contributor history without exposing data accidentally."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

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
            raise ValueError("Church information must be created first.")
        return rows[0][0]

    def date_bounds(self):
        """Return the available Giving date range, or the current year."""
        rows = self.all(
            "SELECT MIN(BatchDate),MAX(BatchDate) FROM tblContributionBatch "
            "WHERE ChurchID=?", (self.church_id(),),
        )
        if rows and rows[0][0] and rows[0][1]:
            return rows[0][0], rows[0][1]
        today = date.today()
        return date(today.year, 1, 1), today

    def contributors(self):
        """Return active and historical contributors for a confidential filter."""
        return self.all(
            "SELECT ID,DisplayName FROM tblContributionContributor "
            "WHERE ChurchID=? ORDER BY DisplayName,ID", (self.church_id(),),
        )

    def batch_summary(self, start_date, end_date):
        """Return donor-free batch controls for the requested period."""
        return self.all(
            "SELECT b.BatchDate,b.Description,o.LegalName,b.Status,b.ControlTotal,"
            "b.CalculatedTotal,(COALESCE(b.ControlTotal,b.CalculatedTotal)-b.CalculatedTotal),"
            "b.AccountingTransactionID FROM tblContributionBatch b "
            "JOIN tblAccountingOrganization o ON o.ID=b.OrganizationID "
            "WHERE b.ChurchID=? AND b.BatchDate BETWEEN ? AND ? "
            "ORDER BY b.BatchDate,b.ID",
            (self.church_id(), start_date, end_date),
        )

    def contributor_history(self, contributor_id, start_date, end_date):
        """Return reviewed or posted allocations for one contributor."""
        return self.all(
            "SELECT g.ReceivedDate,b.Description,g.ContributionMethod,g.ReferenceValue,"
            "COALESCE(p.Name,'Unspecified'),a.Amount,b.Status,g.StatementEligibility "
            "FROM tblContribution g JOIN tblContributionBatch b ON b.ID=g.BatchID "
            "JOIN tblContributionAllocation a ON a.ContributionID=g.ID "
            "LEFT JOIN tblContributionPurpose p ON p.ID=a.PurposeID "
            "WHERE b.ChurchID=? AND g.ContributorID=? "
            "AND g.ReceivedDate BETWEEN ? AND ? AND b.Status IN ('READY','POSTED') "
            "ORDER BY g.ReceivedDate,b.ID,g.ID,a.ID",
            (self.church_id(), contributor_id, start_date, end_date),
        )

    def statement_contributors(self):
        """Return contributors explicitly enabled for contribution statements."""
        return self.all(
            "SELECT ID,COALESCE(NULLIF(StatementName,''),DisplayName) "
            "FROM tblContributionContributor WHERE ChurchID=? AND StatementEnabled=1 "
            "ORDER BY COALESCE(NULLIF(StatementName,''),DisplayName),ID",
            (self.church_id(),),
        )

    def statement_years(self):
        """Return years containing posted contributions, newest first."""
        rows = self.all(
            "SELECT DISTINCT YEAR(g.ReceivedDate) FROM tblContribution g "
            "JOIN tblContributionBatch b ON b.ID=g.BatchID "
            "WHERE b.ChurchID=? AND b.Status='POSTED' ORDER BY 1 DESC",
            (self.church_id(),),
        )
        return [int(row[0]) for row in rows]

    def statement_identity(self, contributor_id):
        """Return the confidential statement name and mailing address."""
        rows = self.all(
            "SELECT ID,COALESCE(NULLIF(StatementName,''),DisplayName),Address,Address2,"
            "City,State,PostalCode FROM tblContributionContributor "
            "WHERE ChurchID=? AND ID=? AND StatementEnabled=1",
            (self.church_id(), contributor_id),
        )
        if not rows:
            raise ValueError("The selected contributor is not enabled for statements.")
        return rows[0]

    def statement_contributors_for_period(self, start_date, end_date):
        """Return enabled contributors having eligible posted gifts in a period."""
        return self.all(
            "SELECT DISTINCT c.ID,COALESCE(NULLIF(c.StatementName,''),c.DisplayName) "
            "FROM tblContributionContributor c JOIN tblContribution g ON g.ContributorID=c.ID "
            "JOIN tblContributionBatch b ON b.ID=g.BatchID "
            "JOIN tblContributionAllocation a ON a.ContributionID=g.ID "
            "LEFT JOIN tblContributionPurpose p ON p.ID=a.PurposeID "
            "WHERE c.ChurchID=? AND c.StatementEnabled=1 AND b.Status='POSTED' "
            "AND g.StatementEligibility='ELIGIBLE' "
            "AND (p.ID IS NULL OR p.StatementTreatment='ELIGIBLE') "
            "AND g.ReceivedDate BETWEEN ? AND ? "
            "ORDER BY COALESCE(NULLIF(c.StatementName,''),c.DisplayName),c.ID",
            (self.church_id(), start_date, end_date),
        )

    def statement_lines(self, contributor_id, start_date, end_date):
        """Return posted, statement-eligible allocation lines for one contributor."""
        return self.all(
            "SELECT g.ReceivedDate,COALESCE(p.Name,'General contribution'),"
            "g.ContributionMethod,a.Amount,g.NonCashDescription,"
            "g.GoodsOrServicesProvided,g.GoodsOrServicesDescription,g.GoodsOrServicesValue,"
            "g.IntangibleReligiousBenefitOnly "
            "FROM tblContribution g JOIN tblContributionBatch b ON b.ID=g.BatchID "
            "JOIN tblContributionAllocation a ON a.ContributionID=g.ID "
            "LEFT JOIN tblContributionPurpose p ON p.ID=a.PurposeID "
            "WHERE b.ChurchID=? AND g.ContributorID=? AND b.Status='POSTED' "
            "AND g.StatementEligibility='ELIGIBLE' "
            "AND (p.ID IS NULL OR p.StatementTreatment='ELIGIBLE') "
            "AND g.ReceivedDate BETWEEN ? AND ? "
            "ORDER BY g.ReceivedDate,g.ID,a.ID",
            (self.church_id(), contributor_id, start_date, end_date),
        )

    def statement_issuance_history(self):
        """Return confidential issued-statement identifiers, newest first."""
        return self.all(
            "SELECT i.GeneratedAt,COALESCE(NULLIF(c.StatementName,''),c.DisplayName),"
            "i.PeriodStart,i.PeriodEnd,i.RevisionNumber,i.OutputFileName,i.DocumentHash "
            "FROM tblContributionStatementIssue i "
            "JOIN tblContributionContributor c ON c.ID=i.ContributorID "
            "WHERE i.ChurchID=? ORDER BY i.GeneratedAt DESC,i.ID DESC",
            (self.church_id(),),
        )

    def record_statement_issuances(self, issues, user_id):
        """Atomically record rendered statement hashes and revision relationships."""
        cursor = self.connection.cursor()
        church_id = self.church_id()
        try:
            for contributor_id, start_date, end_date, version, digest, filename in issues:
                cursor.execute(
                    "SELECT ID,RevisionNumber FROM tblContributionStatementIssue "
                    "WHERE ChurchID=? AND ContributorID=? AND PeriodStart=? AND PeriodEnd=? "
                    "ORDER BY RevisionNumber DESC,ID DESC LIMIT 1 FOR UPDATE",
                    (church_id, contributor_id, start_date, end_date),
                )
                prior = cursor.fetchone()
                revision = (int(prior[1]) + 1) if prior else 1
                cursor.execute(
                    "INSERT INTO tblContributionStatementIssue "
                    "(ChurchID,ContributorID,PeriodStart,PeriodEnd,GeneratedByUserID,TemplateVersion,"
                    "DocumentHash,OutputFileName,RevisionOfID,RevisionNumber) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (church_id, contributor_id, start_date, end_date, int(user_id), version,
                     digest, filename, prior[0] if prior else None, revision),
                )
                issue_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO tblContributionAuditEvent "
                    "(ChurchID,UserID,Action,EntityType,EntityID,SafeReference) "
                    "VALUES (?,?,'STATEMENT_ISSUED','STATEMENT',?,?)",
                    (church_id, int(user_id), issue_id,
                     f"{start_date} through {end_date}; revision {revision}"),
                )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
