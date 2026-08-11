"""
    cm.py - Church Manager
    Rev. Jonathan C. Watt
    Copyright: 2022, Jonathan C. Watt
    July 2022
    
"""
import os
from datetime import datetime, timezone
import wx

import JSForm
import fnSchedule
from application_context import ApplicationContext
from form_factory import ChurchManagerFormFactory
from main_menu import FORM_ROUTES, MENU_CONTROLS, SESSION_CONTROLS
from login_dialog import change_own_password
from authentication import MariaDBUserRepository
from permission_catalog import MAIN_MENU_PERMISSIONS
from backup_service import BackupError, BackupService
from process_service import ProcessService
from report_service import ChurchManagerReportService
from user_admin import show_user_administration
from accounting.setup_dialog import show_accounting_setup
from accounting.draft_dialog import show_accounting_draft_entry
from accounting.review_dialog import show_accounting_review
from accounting.posting_dialog import show_accounting_posting
from accounting.register_dialog import show_accounting_register
from accounting.trial_balance_dialog import show_trial_balance
from accounting.position_dialog import show_financial_position
from accounting.activities_dialog import show_activities
from accounting.bank_import_dialog import show_bank_import
from accounting.audit_dialog import show_accounting_audit
from types import SimpleNamespace


arguments = None
app = None
ChurchDB = None
cmfrm = None
context = None


class clsForm(JSForm.clsForm):
    def bind_form_controls(self):
        JSForm.LG.log()
        if "btnHymnSearchByHymn" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByHymn"],
            )
        if "btnHymnSearchByTitle" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByTitle"],
            )
        if "btnHymnSearchByBible" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByBible"],
            )
        if "btnHymnSearchByCategory" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByCategory"],
            )
        if "btnHymnSearchByNote" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByNote"],
            )
        if "btnHymnSearchAdd" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchAdd"],
            )
        if "btnHymnUsageUpdate" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnusage,
                self.CONTROLID["btnHymnUsageUpdate"],
            )
        if "btnHymnUsageAdd" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON, self._processhymnusage, self.CONTROLID["btnHymnUsageAdd"]
            )
        if "btnAddSermonID" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON, self._addIDtofilename, self.CONTROLID["btnAddSermonID"]
            )
        if "btnAddOutlineID" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON, self._addIDtofilename, self.CONTROLID["btnAddOutlineID"]
            )
        super().bind_form_controls()

    def _checkboxallchecked(self, event):
        JSForm.LG.log()
        field = event.GetEventObject().GetName()
        evnttype = event.GetEventType()
        ID = self.CONTROLID[field].GetValue()
        if len(self.CONTROLID[field].Items) == len(
            self.CONTROLID[field].GetCheckedItems()
        ):
            self.CONTROLID["CheckListComplete"].SetValue(True)
        else:
            self.CONTROLID["CheckListComplete"].SetValue(False)

    def _processhymnsearch(self, event):
        JSForm.LG.log()
        field = event.GetEventObject().GetName()
        eventtype = event.GetEventType()
        if field == "btnHymnSearchAdd":
            if self.CONTROLID["UsedAs"].GetValueText() is None:
                dlg = wx.MessageDialog(self.FORM, "'Used As' cannot be blank")
                dlg.ShowModal()
                dlg.Destroy()
                return
            usedas = self.CONTROLID["UsedAs"].GetValueText()
            row = self.CONTROLID["dvlHymnList"].GetSelectedRow()
            if row is None:
                dlg = wx.MessageDialog(self.FORM, "No Hymn Selected")
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.PARENT.CONTROLID["HymnID"].ChangeValue(row["ID"])
            self.PARENT.CONTROLID["UsedAs"].ChangeValue(usedas)
            self.PARENT.LINKEDFORM.pop("frmHymnSearch")
            try:
                self.FRAME.Destroy()
            except:
                pass
            finally:
                self.FORM.Destroy()

        elif "Search" in self.CONTROLID:
            search = self.CONTROLID["Search"].GetValue()
            if search == "":
                return None
            table = {}
            table["name"] = "tblHymn"
            table["fields"] = ["ID", "Hymn", "Title", "BibleText", "Category", "Note"]
            table["condition"] = "{column} LIKE '%{search}%'"

            if field == "btnHymnSearchByHymn":
                table["condition"] = table["condition"].format(
                    column="Hymn", search=search
                )
            elif field == "btnHymnSearchByTitle":
                table["condition"] = table["condition"].format(
                    column="Title", search=search
                )
            elif field == "btnHymnSearchByBible":
                table["condition"] = table["condition"].format(
                    column="BibleText", search=search
                )
            elif field == "btnHymnSearchByCategory":
                table["condition"] = table["condition"].format(
                    column="Category", search=search
                )
            elif field == "btnHymnSearchByNote":
                table["condition"] = table["condition"].format(
                    column="Note", search=search
                )
            if "dvlHymnList" in self.CONTROLID:
                self.CONTROLID["dvlHymnList"].SetValueTable(table=table)

    def _processhymnusage(self, event):
        JSForm.LG.log()
        field = event.GetEventObject().GetName()
        eventtype = event.GetEventType()
        if field == "btnHymnSearchAdd":
            row = self.CONTROLID["dvlHymnList"].GetSelectedRow()
            self.CONTROLID["dvlHymnUsage"].SetValue(row)
        if field == "btnHymnUsageUpdate":
            row = self.CONTROLID["dvlHymnUsage"].GetSelectedRow()
            self.open_linked_form("frmHymnUsage")

    def _addIDtofilename(self, event):
        global CONFIG
        field = event.GetEventObject().GetName()
        match field:
            case "btnAddSermonID":
                field = "Sermon"
            case "btnAddOutlineID":
                field = "Outline"
        filename = self.CONTROLID[field].GetValue()
        if "ID(" not in filename:
            ID = self.RECORDS._record[self.RECORDS._position]["ID"]
            filename = os.path.splitext(filename)
            newfilename = filename[0] + ".ID(" + str(ID) + ")" + filename[1]
            path = JSForm.CONFIG.get_Config_Value("Location", field)
            os.rename(path + filename[0] + filename[1], path + newfilename)
            self.CONTROLID[field].SetValue(newfilename)

    def _processaction(self, event):
        class _neededoptionsdialog(wx.Dialog):
            def __init__(self, parent, title, formlabel=None):
                super().__init__(parent, title=title, size=(200, 150))
                panel = wx.Panel(self)
                self.text = wx.StaticText(
                    panel,
                    wx.ID_ANY,
                    label=formlabel,
                    pos=(10, 30),
                )
                self.btn = wx.Button(
                    panel,
                    JSForm.CONST.FORM_CONTINUE,
                    label="Continue",
                    size=(100, 30),
                    pos=(10, 75),
                )

        def processattendance(
            field,
        ):
            communion = self.CONTROLID[field].GetCheckedItems()
            attend = self.CONTROLID[field].GetSelections()
            # if (not communion and not attend) and (field == "Members"):
            #    dlg = _neededoptionsdialog(self.FORM, title="Required Field",formlabel="No Attendance Data.")
            #    result = dlg.ShowModal()
            #    dlg.Destroy()
            #    return False

            attrec = []
            for a in range(0, len(attend)):
                attrec.append(
                    {
                        "AttendanceEventID": attendevent,
                        "PersonID": self.CONTROLID[field].choices.id[attend[a]],
                        "Communion": 0,
                    }
                )
            for c in range(0, len(communion)):
                found = False
                for a in range(len(attrec)):
                    if self.CONTROLID[field].choices.id[communion[c]] == (
                        attrec[a]["PersonID"]
                    ):
                        attrec[a]["Communion"] = CommunionOffered == 1
                        found = True
                if not found:
                    attrec.append(
                        {
                            "AttendanceEventID": attendevent,
                            "PersonID": self.CONTROLID[field].choices.id[communion[c]],
                            "Communion": (CommunionOffered == 1),
                        }
                    )

            attendancetable = {
                "name": "tblAttendance",
                "fields": ["PersonID", "AttendanceEventID", "Communion"],
            }

            self.sql = JSForm.clsSQL(self.DBConnection, attendancetable)
            cursor = self.DBConnection.cursor()
            for rec in attrec:
                sql = self.sql.insert(rec)
                try:
                    cursor.execute(sql)
                except:
                    return False
            self.FORM.Close()
            return True

        field = event.GetEventObject().GetName()
        if field == "ReportID":
            rptid = self.CONTROLID[field].GetValue()
            cursor = self.DBConnection.cursor()
            sql = "SELECT Params FROM tblReports WHERE ID={rptid}".format(rptid=rptid)
            try:
                cursor.execute(sql)
            except:
                return None
            row = cursor.fetchone()
            if not row[0]:
                return []
            params = row[0]
            self.disable_all_buttons()
            self.enable_button("ChurchID")
            self.enable_button("ReportID")
            self.enable_button("btnRun")
            self.enable_button("btnClose")
            params = row[0].replace("[", "")
            params = params.replace("]", "")
            params = params.replace(",", "")
            params = params.splitlines()
            self.enable_buttons(params)
            return

        attendevent = self.CONTROLID["AttendanceEventID"].GetValue()
        if not attendevent:
            dlg = _neededoptionsdialog(
                self.FORM,
                title="Required Field",
                formlabel="Attendance Event not entered.",
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        sql = "SELECT CommunionOffered FROM tblAttendanceEvent WHERE ID = {AttenanceEventID}".format(
            AttenanceEventID=attendevent
        )
        cursor = self.DBConnection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        CommunionOffered = row[0]
        if not processattendance("Members"):
            return
        if not processattendance("Visitors"):
            return


##  Main App    ##


def _buttonclick(event):
    def _runSPrpt(event):
        context.services.reports.run_catalog_report(2, frm, context.connection)

    def _runOSrpt(event):
        ID = frm.CONTROLID["ServiceID"].GetValue()
        if ID == None:
            return
        context.services.reports.start_python_report(
            "rptOrderofService.py", arguments, ["--ID", str(ID)]
        )
        frm.FORM.Close()

    def _runSchedule(event):
        ID = int(frm.CONTROLID["ServiceID"].GetValue())
        if ID == None:
            return
        fnSchedule.ScheduleParticipants(ID, ChurchDB.DBConnection)

    def _runNotify(event):
        ID = int(frm.CONTROLID["ServiceID"].GetValue())
        if ID == None:
            return
        #JSForm.RunReport(2, frm, ChurchDB.DBConnection)
        fnSchedule.notifyviaeMail(ID, ChurchDB.DBConnection)
        frm.FORM.Close()

    def _runPrayerRequests():
        reportdescription = JSForm.CONFIG.get_Config_Value(
            "Location", "ReportDescription"
        )
        report = JSForm.CONFIG.get_Config_Value("Location", "Report")
        limedir = JSForm.CONFIG.get_Config_Value("Location", "LimeReport")
        source_template = "{reportdescription}CMPR01.lrxml".format(reportdescription=reportdescription)
        context.services.reports.run_lime_report(
            source_template, "{report}CMPR01.pdf".format(report=report),
            arguments["database"], limedir,
        )

    def _runSundayPrayers():
        context.services.reports.start_python_report(
            "rptPrayers.py", arguments, ["--reportdate", "now"]
        )

    def _runSundayAnnouncements():
        context.services.reports.start_python_report(
            "rptAnnouncement.py", arguments, ["--reportdate", "now"]
        )

    def _runReports(event):
        reportid = frm.CONTROLID["ReportID"].GetValue()
        context.services.reports.run_catalog_report(reportid, frm, context.connection)
        frm.FORM.Close()

    def _runBackupDB():
        class _backupcomplete(wx.Dialog):
            def __init__(self, parent, title, formlabel=None):
                super().__init__(parent, title=title, size=(200, 150))
                panel = wx.Panel(self)
                self.text = wx.StaticText(
                    panel,
                    wx.ID_ANY,
                    label=formlabel,
                    pos=(10, 30),
                )
                self.btn = wx.Button(
                    panel,
                    JSForm.CONST.FORM_CONTINUE,
                    label="Ok",
                    size=(100, 30),
                    pos=(10, 75),
                )

        mysqldump = JSForm.CONFIG.get_Config_Value("Location", "MySQLDump")
        dbbackup = JSForm.CONFIG.get_Config_Value("Location", "DBBackup")
        try:
            result = context.services.backups.create(arguments, mysqldump, dbbackup)
        except BackupError as error:
            wx.MessageBox(str(error), "Backup failed", wx.OK | wx.ICON_ERROR)
            return
        JSForm.OPTION.set_Option_Value("Backup", "LastDate", result.timestamp)
        dlg = _backupcomplete(
            None,
            title="Backup Complete",
            formlabel="Backup Complete.\n{stamp}".format(stamp=result.timestamp),
        )
        result = dlg.ShowModal()
        dlg.Destroy()

    select = event.GetEventObject().GetName()
    if select == "lblChangePassword":
        change_own_password(
            context.connection, context.session, cmfrm.FRAME,
            minimum_length=4 if context.test_mode else 12,
        )
        return
    if select == "lblLogout":
        MariaDBUserRepository(context.connection).record_auth_event(
            context.session.user_id,
            "LOGOUT",
            context.session.workstation,
            datetime.now(timezone.utc).replace(tzinfo=None),
            context.session.username,
        )
        cmfrm.FRAME.Close()
        return
    context.authorization.require(
        MAIN_MENU_PERMISSIONS[select], "use {}".format(select)
    )
    if select in FORM_ROUTES:
        context.form_factory.open(FORM_ROUTES[select])
        return
    match select:
        case "lblGenerateOS":
            frm = context.form_factory.create("frmGenerateOS", ["Close"])
            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runOSrpt)
            frm.show()
            return
        case "lblNotifyParticipants":
            frm = context.form_factory.create("frmNotifyviaeMail")
            frm.CONTROLID["btnNotify"].Bind(wx.EVT_LEFT_DOWN, _runNotify)
            frm.show()
            return
        case "lblSundayPrayers":
            _runSundayPrayers()
        case "lblAnnouncements":
            _runSundayAnnouncements()
        case "lblServiceSchedule":
            frm = context.form_factory.create(
                "frmServiceSchedule", ["Navigation", "Close"]
            )
            frm.CONTROLID["btnRunSchedule"].Bind(wx.EVT_LEFT_DOWN, _runSchedule)
            frm.show()
            return
        case "lblReports":
            frm = context.form_factory.create("frmReports", ["Close"])
            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runReports)
            frm.disable_all_buttons()
            frm.enable_button("ReportID")
            frm.enable_button("btnRun")
            frm.enable_button("btnClose")
            frm.show()
            return
        case "lblBackupDB":
            _runBackupDB()
        case "lblUsers":
            show_user_administration(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
                minimum_length=4 if context.test_mode else 12,
            )
        case "lblAccountingSetup":
            show_accounting_setup(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingTransactions":
            show_accounting_draft_entry(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
                test_mode=context.test_mode,
            )
        case "lblAccountingReview":
            show_accounting_review(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingPosting":
            show_accounting_posting(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingRegister":
            show_accounting_register(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingTrialBalance":
            show_trial_balance(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingPosition":
            show_financial_position(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingActivities":
            show_activities(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingBankImport":
            show_bank_import(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingAudit":
            show_accounting_audit(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case _:
            raise KeyError("No ChurchManager menu route for {}".format(select))


def main(argv=None):
    global arguments, app, ChurchDB, cmfrm, context
    from startup import build_runtime

    runtime = build_runtime(clsForm, argv)
    arguments = runtime.arguments
    app = runtime.wx_app
    ChurchDB = runtime.database
    cmfrm = runtime.main_form
    context = ApplicationContext(
        arguments, ChurchDB, cmfrm,
        session=runtime.session, authorization=runtime.authorization,
    )
    context.form_factory = ChurchManagerFormFactory(
        clsForm, context.connection, cmfrm,
        authorization_policy=context.authorization,
    )
    processes = ProcessService()
    context.services = SimpleNamespace(
        processes=processes,
        backups=BackupService(),
        reports=ChurchManagerReportService(JSForm, processes),
    )

    for control_name in MENU_CONTROLS:
        if control_name in cmfrm.CONTROLID:
            cmfrm.CONTROLID[control_name].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
    if context.session is not None:
        for control_name in SESSION_CONTROLS:
            cmfrm.CONTROLID[control_name].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
        cmfrm.CONTROLID["lblCurrentUser"].SetLabel(
            "Signed in: {}".format(context.session.display_name)
        )
    else:
        for control_name in SESSION_CONTROLS | {"lblCurrentUser", "SessionBox"}:
            cmfrm.CONTROLID[control_name].Hide()

    cmfrm.show()
    app.MainLoop()


if __name__ == "__main__":
    main()
