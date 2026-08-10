"""Atomic creation of a reviewed starter accounting configuration."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

from .starter_data import STARTER_ACCOUNTS, STARTER_FUNDS, STARTER_FUNCTIONS


VALID_NET_ASSET_CLASSES = {
    "WITHOUT_DONOR_RESTRICTIONS", "WITH_DONOR_RESTRICTIONS",
}
VALID_RESTRICTION_TYPES = {"NONE", "PURPOSE", "TIME", "PURPOSE_AND_TIME"}


@dataclass(frozen=True)
class FundClassification:
    net_asset_class: str
    restriction_type: str
    board_designated: bool = False


def calendar_periods(year):
    year = int(year)
    return tuple(
        (
            month,
            calendar.month_name[month],
            date(year, month, 1),
            date(year, month, calendar.monthrange(year, month)[1]),
        )
        for month in range(1, 13)
    )


def validated_fund_classifications(classifications):
    classifications = dict(classifications or {})
    required = {fund.code for fund in STARTER_FUNDS if fund.requires_classification}
    missing = sorted(required - set(classifications))
    if missing:
        raise ValueError(
            "Classify these special-purpose funds before setup: {}.".format(
                ", ".join(missing)
            )
        )
    result = {}
    for fund in STARTER_FUNDS:
        selected = classifications.get(fund.code)
        if selected is None:
            selected = FundClassification(
                fund.net_asset_class, fund.restriction_type, fund.board_designated
            )
        if selected.net_asset_class not in VALID_NET_ASSET_CLASSES:
            raise ValueError("{} has an invalid net-asset class.".format(fund.name))
        if selected.restriction_type not in VALID_RESTRICTION_TYPES:
            raise ValueError("{} has an invalid restriction type.".format(fund.name))
        if (
            selected.net_asset_class == "WITH_DONOR_RESTRICTIONS"
            and selected.board_designated
        ):
            raise ValueError(
                "{} cannot be both donor-restricted and board-designated.".format(
                    fund.name
                )
            )
        if (
            selected.net_asset_class == "WITHOUT_DONOR_RESTRICTIONS"
            and selected.restriction_type != "NONE"
        ):
            raise ValueError(
                "{} cannot have a donor restriction type without donor restrictions.".format(
                    fund.name
                )
            )
        result[fund.code] = selected
    return result


class AccountingSetupService:
    def __init__(self, connection, acting_user_id):
        self.connection = connection
        self.acting_user_id = acting_user_id
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def create_starter_organization(
        self, legal_name, fiscal_year, fund_classifications, church_id=None
    ):
        legal_name = (legal_name or "").strip()
        if not legal_name:
            raise ValueError("Organization legal name is required.")
        year = int(fiscal_year)
        classifications = validated_fund_classifications(fund_classifications)
        periods = calendar_periods(year)
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT COUNT(*) FROM tblAccountingOrganization "
                "WHERE LegalName=? AND Active=1",
                (legal_name,),
            )
            if cursor.fetchone()[0]:
                raise ValueError("An active accounting organization with that name already exists.")
            self._execute(
                cursor,
                "INSERT INTO tblAccountingOrganization "
                "(ChurchID, LegalName, FiscalYearStartMonth, BaseCurrency, "
                "ReportingBasis, ApprovalThreshold, AttachmentThreshold) "
                "VALUES (?, ?, 1, 'USD', 'MODIFIED_CASH', 500.00, 250.00)",
                (church_id, legal_name),
            )
            organization_id = cursor.lastrowid

            account_ids = {}
            for display_order, account in enumerate(STARTER_ACCOUNTS, start=1):
                self._execute(
                    cursor,
                    "INSERT INTO tblAccountingAccount "
                    "(OrganizationID, Code, Name, AccountType, NormalBalance, "
                    "FunctionRequirement, DisplayOrder, Active) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        organization_id, account.code, account.name,
                        account.account_type, account.normal_balance,
                        account.function_requirement, display_order,
                        int(account.active),
                    ),
                )
                account_ids[account.code] = cursor.lastrowid

            for fund in STARTER_FUNDS:
                selected = classifications[fund.code]
                net_asset_code = (
                    "3200" if selected.net_asset_class == "WITH_DONOR_RESTRICTIONS"
                    else "3100" if selected.board_designated else "3000"
                )
                self._execute(
                    cursor,
                    "INSERT INTO tblAccountingFund "
                    "(OrganizationID, Code, Name, NetAssetClass, RestrictionType, "
                    "BoardDesignated, NetAssetAccountID, Active) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        organization_id, fund.code, fund.name,
                        selected.net_asset_class, selected.restriction_type,
                        int(selected.board_designated), account_ids[net_asset_code],
                        int(fund.active),
                    ),
                )

            for display_order, function in enumerate(STARTER_FUNCTIONS, start=1):
                self._execute(
                    cursor,
                    "INSERT INTO tblAccountingFunction "
                    "(OrganizationID, Code, Name, FunctionClass, DisplayOrder) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        organization_id, function.code, function.name,
                        function.function_class, display_order,
                    ),
                )

            self._execute(
                cursor,
                "INSERT INTO tblAccountingFiscalYear "
                "(OrganizationID, Name, StartDate, EndDate, Status) "
                "VALUES (?, ?, ?, ?, 'OPEN')",
                (organization_id, str(year), periods[0][2], periods[-1][3]),
            )
            fiscal_year_id = cursor.lastrowid
            for number, name, start_date, end_date in periods:
                self._execute(
                    cursor,
                    "INSERT INTO tblAccountingFiscalPeriod "
                    "(FiscalYearID, PeriodNumber, Name, StartDate, EndDate, Status) "
                    "VALUES (?, ?, ?, ?, ?, 'OPEN')",
                    (fiscal_year_id, number, name, start_date, end_date),
                )

            self._execute(
                cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID, EntityType, EntityID, Action, Reason, UserID) "
                "VALUES (?, 'Organization', ?, 'ACCOUNTING_SETUP_CREATED', "
                "'Congregation-neutral starter configuration', ?)",
                (organization_id, str(organization_id), self.acting_user_id),
            )
            self.connection.commit()
            return organization_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
