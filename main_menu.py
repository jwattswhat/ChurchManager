"""Menu routing independent of wxPython and database access."""


FORM_ROUTES = {
    "lblChurch": "frmChurch",
    "lblSermon": "frmSermon",
    "lblHymnal": "frmHymnal",
    "lblHymn": "frmHymn",
    "lblFamily": "frmFamily",
    "lblPerson": "frmPerson",
    "lblConfig": "frmConfig",
    "lblOptions": "frmOptions",
    "lblJournal": "frmJournal",
    "lblDocument": "frmDocument",
    "lblAccountingAccounts": "frmAccountingAccount",
    "lblAccountingFunds": "frmAccountingFund",
    "lblAccountingFunctions": "frmAccountingFunction",
    "lblAccountingYears": "frmAccountingFiscalYear",
    "lblAccountingPeriods": "frmAccountingFiscalPeriod",
    "lblAccountingBankAccounts": "frmAccountingBankAccount",
    "lblAccountingPayees": "frmAccountingPayee",
}

SPECIAL_CONTROLS = {
    "lblService", "lblOS", "lblCheckList", "lblWeeklyBulletinOrder", "lblGenerateOS", "lblNotifyParticipants", "lblSundayPrayers",
    "lblParticipant", "lblWorshipPositions", "lblSchedule", "lblPrayers", "lblAnnouncement", "lblChoices",
    "lblAnnouncements", "lblServiceSchedule", "lblReports", "lblReportDesigner", "lblScreenDesigner", "lblBackupDB",
    "lblUsers", "lblEmailSettings", "lblSupportDiagnostics", "lblLectionaryPackages", "lblPropers", "lblAttendanceEvent", "lblRecordAttendance",
    "lblAccountingSetup",
    "lblAccountingTransactions",
    "lblAccountingReview",
    "lblAccountingPosting",
    "lblAccountingRegister",
    "lblAccountingTrialBalance",
    "lblAccountingPosition",
    "lblAccountingActivities",
    "lblAccountingBankImport",
    "lblAccountingAudit",
    "lblAccountingGeneralLedger",
    "lblAccountingFundBalances",
    "lblAccountingReconciliationReport",
    "lblAccountingCloseChecklist",
    "lblAccountingBudgets",
    "lblAccountingBudgetActual",
    "lblAccountingFunctionalExpenses",
    "lblAccountingYearEnd",
    "lblGivingContributors",
    "lblGivingPurposes",
    "lblContributionBatches",
    "lblGivingReports",
    "lblPastoralCare", "lblDataManagement", "lblGroups", "lblGroupAttendance", "lblCustomProfileFields", "lblCustomProfileSearch",
    "lblCalendarEvents", "lblCalendarIntegration", "lblAssets", "lblAssetLocations", "lblAssetMaintenance", "lblAssetReports", "lblProjects",
}
MENU_CONTROLS = frozenset(FORM_ROUTES) | SPECIAL_CONTROLS
SESSION_CONTROLS = frozenset({"lblHelp", "lblChangePassword", "lblLogout"})


# Stable command labels are application metadata, not screen-definition data.
# Menu commands remain available even when their action is intentionally absent
# from the compact daily-work dashboard.
MENU_LABELS = {
    'lblAccountingAccounts': 'Chart of Accounts',
    'lblAccountingActivities': 'Statement of Activities',
    'lblAccountingAudit': 'Audit History',
    'lblAccountingBankAccounts': 'Bank Accounts',
    'lblAccountingBankImport': 'Bank File Import',
    'lblAccountingBudgetActual': 'Budget to Actual',
    'lblAccountingBudgets': 'Budgets',
    'lblAccountingCloseChecklist': 'Close Checklist',
    'lblAccountingFunctionalExpenses': 'Functional Expenses',
    'lblAccountingFunctions': 'Functional Classifications',
    'lblAccountingFundBalances': 'Fund Balances',
    'lblAccountingFunds': 'Funds and Restrictions',
    'lblAccountingGeneralLedger': 'General Ledger',
    'lblAccountingPayees': 'Payees',
    'lblAccountingPeriods': 'Fiscal Periods',
    'lblAccountingPosition': 'Financial Position',
    'lblAccountingPosting': 'Transaction Posting',
    'lblAccountingReconciliationReport': 'Reconciliation Report',
    'lblAccountingRegister': 'Posted Register',
    'lblAccountingReview': 'Transaction Review',
    'lblAccountingSetup': 'Accounting Setup',
    'lblAccountingTransactions': 'Transaction Entry',
    'lblAccountingTrialBalance': 'Trial Balance',
    'lblAccountingYearEnd': 'Year-End Close',
    'lblAccountingYears': 'Fiscal Years',
    'lblAnnouncement': 'Announcements',
    'lblAnnouncements': 'Weekly Announcements',
    'lblAttendanceEvent': 'Attendance Events',
    'lblBackupDB': 'Database Backup and Restore',
    'lblCalendarEvents': 'Events',
    'lblCalendarIntegration': 'Calendar Integration',
    'lblCheckList': 'Preparation Checklists',
    'lblChoices': 'Choices',
    'lblChurch': 'Church Information',
    'lblConfig': 'Configuration',
    'lblContributionBatches': 'Contribution Batches',
    'lblCustomProfileFields': 'Custom Profile Fields',
    'lblCustomProfileSearch': 'Custom Profile Search',
    'lblDataManagement': 'Data Management',
    'lblDocument': 'Documents',
    'lblEmailSettings': 'Email Settings',
    'lblFamily': 'Families',
    'lblGenerateOS': 'Prepare Bulletin Order',
    'lblGivingContributors': 'Contributors and Envelopes',
    'lblGivingPurposes': 'Approved Giving Purposes',
    'lblGivingReports': 'Giving Reports',
    'lblGroupAttendance': 'Group Attendance',
    'lblGroups': 'Groups',
    'lblHymn': 'Hymns',
    'lblHymnal': 'Hymnals',
    'lblJournal': 'Journal',
    'lblLectionaryPackages': 'Lectionary Packages',
    'lblNotifyParticipants': 'Notify Participants',
    'lblOS': 'Bulletin Order Templates',
    'lblOptions': 'Options',
    'lblParticipant': 'Participants',
    'lblPastoralCare': 'Pastoral Follow-ups',
    'lblPerson': 'People',
    'lblPrayers': 'Prayers',
    'lblPropers': 'Local Lectionaries',
    'lblRecordAttendance': 'Record Attendance',
    'lblReportDesigner': 'Report Designer',
    'lblReports': 'Reports',
    'lblSchedule': 'Scheduling Patterns',
    'lblScreenDesigner': 'Screen Designer',
    'lblSermon': 'Sermons',
    'lblService': 'Worship Services',
    'lblServiceSchedule': 'Service Participants',
    'lblSundayPrayers': 'Weekly Prayers',
    'lblSupportDiagnostics': 'Support and Diagnostics',
    'lblUsers': 'Users and Roles',
    'lblWeeklyBulletinOrder': 'Weekly Bulletin Order',
    'lblWorshipPositions': 'Worship Positions',
    'lblAssets': 'Assets',
    'lblAssetLocations': 'Asset Locations',
    'lblAssetMaintenance': 'Maintenance Due',
    'lblAssetReports': 'Asset Reports',
    'lblProjects': 'Projects and Scheduling',
}


def command_name(control_name):
    """Return the stable JSForm command name for one ChurchManager action."""
    stem = control_name[3:] if control_name.startswith("lbl") else control_name
    import re
    words = re.sub(r"(?<!^)(?=[A-Z])", "_", stem).lower()
    return "churchmanager.{}".format(words)


class MainMenuRouter:
    def __init__(self, form_factory, special_handlers=None):
        self.form_factory = form_factory
        self.special_handlers = special_handlers or {}

    def dispatch(self, control_name):
        if control_name in FORM_ROUTES:
            return self.form_factory.open(FORM_ROUTES[control_name])
        handler = self.special_handlers.get(control_name)
        if handler:
            return handler()
        raise KeyError("No ChurchManager menu route for {}".format(control_name))
