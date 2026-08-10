"""Congregation-neutral starter accounting configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountTemplate:
    code: str
    name: str
    account_type: str
    normal_balance: str
    function_requirement: str = "PROHIBITED"
    active: bool = True


@dataclass(frozen=True)
class FundTemplate:
    code: str
    name: str
    net_asset_class: str | None
    restriction_type: str | None
    board_designated: bool = False
    active: bool = True

    @property
    def requires_classification(self):
        return self.net_asset_class is None


@dataclass(frozen=True)
class FunctionTemplate:
    code: str
    name: str
    function_class: str = "PROGRAM"


STARTER_ACCOUNTS = (
    AccountTemplate("1000", "Checking", "ASSET", "DEBIT"),
    AccountTemplate("1100", "Savings", "ASSET", "DEBIT"),
    AccountTemplate("1200", "Accounts Receivable", "ASSET", "DEBIT", active=False),
    AccountTemplate("1300", "Prepaid Expenses", "ASSET", "DEBIT"),
    AccountTemplate("1500", "Property and Equipment", "ASSET", "DEBIT"),
    AccountTemplate("1590", "Accumulated Depreciation", "ASSET", "CREDIT", active=False),
    AccountTemplate("2000", "Accounts Payable", "LIABILITY", "CREDIT", active=False),
    AccountTemplate("2100", "Payroll and Other Withholdings", "LIABILITY", "CREDIT"),
    AccountTemplate("2200", "Accrued Expenses", "LIABILITY", "CREDIT"),
    AccountTemplate("2300", "Deferred Revenue", "LIABILITY", "CREDIT", active=False),
    AccountTemplate("2500", "Loans Payable", "LIABILITY", "CREDIT"),
    AccountTemplate("3000", "Net Assets Without Donor Restrictions", "NET_ASSET", "CREDIT"),
    AccountTemplate("3100", "Board-Designated Net Assets", "NET_ASSET", "CREDIT"),
    AccountTemplate("3200", "Net Assets With Donor Restrictions", "NET_ASSET", "CREDIT"),
    AccountTemplate("4000", "General Contributions", "REVENUE", "CREDIT", "OPTIONAL"),
    AccountTemplate("4100", "Restricted Contributions", "REVENUE", "CREDIT", "OPTIONAL"),
    AccountTemplate("4200", "Grants", "REVENUE", "CREDIT", "OPTIONAL"),
    AccountTemplate("4300", "Program and Event Income", "REVENUE", "CREDIT", "OPTIONAL"),
    AccountTemplate("4400", "Interest and Investment Income", "REVENUE", "CREDIT", "OPTIONAL"),
    AccountTemplate("4900", "Other Income", "REVENUE", "CREDIT", "OPTIONAL"),
    AccountTemplate("5000", "Pastoral Compensation", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5100", "Other Salaries and Wages", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5200", "Employee Benefits", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5300", "Worship", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5400", "Christian Education", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5500", "Missions and Benevolence", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5600", "Property and Utilities", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5700", "Office and Administration", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5800", "Insurance and Professional Services", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("5900", "Fundraising", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("6000", "Depreciation", "EXPENSE", "DEBIT", "REQUIRED", False),
    AccountTemplate("6900", "Other Expenses", "EXPENSE", "DEBIT", "REQUIRED"),
    AccountTemplate("8000", "Transfers Out", "TRANSFER", "DEBIT"),
    AccountTemplate("8100", "Transfers In", "TRANSFER", "CREDIT"),
)


STARTER_FUNDS = (
    FundTemplate("GENERAL", "General Operating", "WITHOUT_DONOR_RESTRICTIONS", "NONE"),
    FundTemplate("RESERVE", "Operating Reserve", "WITHOUT_DONOR_RESTRICTIONS", "NONE", True),
    FundTemplate("BUILDING", "Building / Capital Projects", None, None),
    FundTemplate("MISSIONS", "Missions / Outreach", None, None),
    FundTemplate("BENEVOLENCE", "Benevolence", None, None),
    FundTemplate("MEMORIALS", "Memorials / Special Gifts", None, None),
    FundTemplate("ENDOWMENT", "Endowment", None, None, active=False),
)


STARTER_FUNCTIONS = (
    FunctionTemplate("WORSHIP", "Worship"),
    FunctionTemplate("EDUCATION", "Christian Education"),
    FunctionTemplate("OUTREACH", "Outreach and Missions"),
    FunctionTemplate("MERCY", "Pastoral Care and Mercy"),
    FunctionTemplate("FELLOWSHIP", "Fellowship"),
    FunctionTemplate("MGMT", "Management and General", "MANAGEMENT_GENERAL"),
    FunctionTemplate("FUNDRAISING", "Fundraising", "FUNDRAISING"),
)
