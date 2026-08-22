"""Resolve parsed contribution rows into a non-writing import preview."""

from __future__ import annotations

from dataclasses import dataclass

from bulletin_orders import portable_connection
from giving.import_parser import ContributionImportRow


@dataclass(frozen=True)
class ContributionPreviewRow:
    """A parsed import row with resolved identifiers and actionable issues."""

    source: ContributionImportRow
    contributor_id: int | None
    purpose_id: int | None
    issues: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return true only when this row can safely enter a draft batch."""
        return not self.issues


class ContributionImportPreviewService:
    """Validate identities, purposes, and duplicates without changing data."""

    def __init__(self, connection, church_id: int, organization_id: int):
        self.connection = portable_connection(connection)
        self.church_id = int(church_id)
        self.organization_id = int(organization_id)

    def all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def preview(self, rows) -> tuple[ContributionPreviewRow, ...]:
        """Return a complete preview; this method performs SELECT statements only."""
        rows = tuple(rows)
        file_counts = {}
        for row in rows:
            file_counts[row.fingerprint] = file_counts.get(row.fingerprint, 0) + 1
        return tuple(self._preview_row(row, file_counts[row.fingerprint] > 1) for row in rows)

    def _preview_row(self, row: ContributionImportRow, repeated_in_file: bool):
        issues = []
        envelope_id = self._envelope_contributor(row)
        named_id = self._named_contributor(row)
        if row.envelope_number and envelope_id is None:
            issues.append("Unknown envelope")
        if row.contributor and named_id is None:
            issues.append("Unknown contributor")
        if envelope_id is not None and named_id is not None and envelope_id != named_id:
            issues.append("Envelope and contributor disagree")
        contributor_id = envelope_id if envelope_id is not None else named_id
        purpose_id = self._purpose(row)
        if not row.purpose:
            issues.append("Purpose is required")
        elif purpose_id is None:
            issues.append("Unknown or inactive purpose")
        if repeated_in_file:
            issues.append("Duplicate row in file")
        if self._already_imported(row):
            issues.append("Possible existing contribution")
        return ContributionPreviewRow(row, contributor_id, purpose_id, tuple(issues))

    def _envelope_contributor(self, row):
        if not row.envelope_number:
            return None
        records = self.all(
            "SELECT e.ContributorID FROM tblContributionEnvelopeAssignment e "
            "JOIN tblContributionContributor c ON c.ID=e.ContributorID "
            "WHERE e.ChurchID=? AND e.EnvelopeNumber REGEXP '^[0-9]+$' "
            "AND CAST(e.EnvelopeNumber AS UNSIGNED)=? AND e.EffectiveFrom<=? "
            "AND (e.EffectiveThrough IS NULL OR e.EffectiveThrough>=?) AND c.IsActive=1 "
            "ORDER BY e.EffectiveFrom DESC,e.ID DESC LIMIT 2",
            (self.church_id, int(row.envelope_number), row.received_date, row.received_date),
        )
        return records[0][0] if len(records) == 1 else None

    def _named_contributor(self, row):
        if not row.contributor:
            return None
        records = self.all(
            "SELECT ID FROM tblContributionContributor WHERE ChurchID=? AND IsActive=1 "
            "AND DisplayName=? COLLATE utf8mb4_unicode_ci ORDER BY ID LIMIT 2",
            (self.church_id, row.contributor),
        )
        return records[0][0] if len(records) == 1 else None

    def _purpose(self, row):
        if not row.purpose:
            return None
        records = self.all(
            "SELECT ID FROM tblContributionPurpose WHERE ChurchID=? AND OrganizationID=? "
            "AND IsActive=1 AND Name=? COLLATE utf8mb4_unicode_ci AND EffectiveFrom<=? "
            "AND (EffectiveThrough IS NULL OR EffectiveThrough>=?) ORDER BY ID LIMIT 2",
            (self.church_id, self.organization_id, row.purpose,
             row.received_date, row.received_date),
        )
        return records[0][0] if len(records) == 1 else None

    def _already_imported(self, row):
        if not row.reference:
            return False
        records = self.all(
            "SELECT g.ID FROM tblContribution g JOIN tblContributionBatch b ON b.ID=g.BatchID "
            "WHERE b.ChurchID=? AND g.ReceivedDate=? AND g.Amount=? "
            "AND g.ContributionMethod=? AND g.ReferenceValue=? LIMIT 1",
            (self.church_id, row.received_date, row.amount, row.method, row.reference),
        )
        return bool(records)
