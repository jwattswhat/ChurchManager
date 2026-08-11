"""Menu routing independent of wxPython and database access."""


FORM_ROUTES = {
    "lblChurch": "frmChurch",
    "lblService": "frmService",
    "lblSermon": "frmSermon",
    "lblPropers": "frmPropers",
    "lblPrayers": "frmPrayer",
    "lblOSList": "frmOSList",
    "lblOS": "frmOS",
    "lblCheckList": "frmCheckList",
    "lblEnhancements": "frmEnhancement",
    "lblFamily": "frmFamily",
    "lblPerson": "frmPerson",
    "lblAttendanceEvent": "frmAttendanceEvent",
    "lblRecordAttendance": "frmRecordAttendance",
    "lblParticipant": "frmParticipant",
    "lblSchedule": "frmSchedule",
    "lblConfig": "frmConfig",
    "lblOptions": "frmOptions",
    "lblChoices": "frmChoices",
    "lblJournal": "frmJournal",
    "lblProject": "frmProject",
    "lblTask": "frmTask",
    "lblDocument": "frmDocument",
    "lblAnnouncement": "frmAnnouncement",
    "lblAccountingAccounts": "frmAccountingAccount",
    "lblAccountingFunds": "frmAccountingFund",
    "lblAccountingFunctions": "frmAccountingFunction",
    "lblAccountingYears": "frmAccountingFiscalYear",
    "lblAccountingPeriods": "frmAccountingFiscalPeriod",
    "lblAccountingBankAccounts": "frmAccountingBankAccount",
    "lblAccountingPayees": "frmAccountingPayee",
}

SPECIAL_CONTROLS = {
    "lblGenerateOS", "lblNotifyParticipants", "lblSundayPrayers",
    "lblAnnouncements", "lblServiceSchedule", "lblReports", "lblBackupDB",
    "lblUsers",
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
}
MENU_CONTROLS = frozenset(FORM_ROUTES) | SPECIAL_CONTROLS
SESSION_CONTROLS = frozenset({"lblChangePassword", "lblLogout"})


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
