"""
    cm.py - Church Manager
    Rev. Jonathan C. Watt
    Copyright: 2022, Jonathan C. Watt
    July 2022
    
"""
import os
import subprocess
import sys
from pathlib import Path
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
from backup_restore_dialog import show_backup_restore, run_automatic_exit_backup
from process_service import ProcessService
from report_service import ChurchManagerReportService
from report_access import ReportAccessService
from visual_reports.designer import open_directory_designer
from churchmanager_screen_designer import open_churchmanager_screen_designer
from user_admin import show_user_administration
from bulletin_order_dialog import show_bulletin_orders
from bulletin_order_generator_dialog import show_prepare_bulletin_order
from weekly_bulletin_order_dialog import show_weekly_bulletin_order
from worship_service_dialog import show_worship_services
from worship_checklist import show_checklist_maintenance
from worship_scheduling import (
    show_participants, show_schedule_patterns, show_service_participants,
)
from sunday_content_dialog import show_announcements, show_prayers, show_sunday_preview
from report_support import get_today, load_report_config
from JSForm.choice_manager import show_choice_manager
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
from accounting.general_ledger_dialog import show_general_ledger
from accounting.fund_balance_dialog import show_fund_balances
from accounting.reconciliation_report_dialog import show_reconciliation_report
from accounting.close_checklist_dialog import show_close_checklist
from accounting.budget_dialog import show_budgets
from accounting.budget_actual_dialog import show_budget_actual
from accounting.functional_expense_dialog import show_functional_expenses
from accounting.year_end_dialog import show_year_end
from types import SimpleNamespace
from single_instance import ChurchManagerSingleInstance


arguments = None
app = None
ChurchDB = None
cmfrm = None
context = None
single_instance = None


class clsForm(JSForm.clsForm):
    def _refresh_parent_grid(self, control_name):
        parent = self.PARENT
        if not parent or control_name not in getattr(parent, "CONTROLID", {}):
            return
        if not getattr(parent, "RECORDS", None):
            return
        description = parent.CONTROLDESCRIPTION[control_name]
        parent.CONTROLID[control_name].SetValueTable(
            parent.RECORDS.current(), description["table"]
        )

    def _on_close(self, event):
        refresh_suggestions = self.FORMNAME == "frmProperHymnSuggestion"
        refresh_hymn_choices = self.FORMNAME == "frmHymn"
        super()._on_close(event)
        if refresh_suggestions:
            wx.CallAfter(self._refresh_parent_grid, "dvlHymnSuggestions")
        if refresh_hymn_choices and getattr(self, "PARENT", None):
            wx.CallAfter(self.PARENT.update_choices)

    def bind_form_controls(self):
        JSForm.LG.log()
        if "btnAddSermonID" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON, self._addIDtofilename, self.CONTROLID["btnAddSermonID"]
            )
        if "btnAddOutlineID" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON, self._addIDtofilename, self.CONTROLID["btnAddOutlineID"]
            )
        super().bind_form_controls()

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
        show_sunday_preview(
            cmfrm.FRAME, context.connection, "prayer", get_today(load_report_config()),
            lambda value, church_id: context.services.reports.start_python_report(
                "rptPrayers.py", arguments, ["--reportdate", value.isoformat(), "--church-id", str(church_id)]
            ),
        )

    def _runSundayAnnouncements():
        show_sunday_preview(
            cmfrm.FRAME, context.connection, "announcement", get_today(load_report_config()),
            lambda value, church_id: context.services.reports.start_python_report(
                "rptAnnouncement.py", arguments, ["--reportdate", value.isoformat(), "--church-id", str(church_id)]
            ),
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
    if select == "lblService":
        show_worship_services(
            cmfrm.FRAME, context.connection, context.form_factory, context.session,
        )
        return
    if select in FORM_ROUTES:
        context.form_factory.open(FORM_ROUTES[select])
        return
    match select:
        case "lblCheckList":
            show_checklist_maintenance(cmfrm.FRAME, context.connection)
            return
        case "lblOS":
            show_bulletin_orders(cmfrm.FRAME, context.connection)
            return
        case "lblWeeklyBulletinOrder":
            show_weekly_bulletin_order(cmfrm.FRAME, context.connection)
            return
        case "lblParticipant":
            show_participants(cmfrm.FRAME, context.connection)
            return
        case "lblPrayers":
            show_prayers(cmfrm.FRAME, context.connection)
            return
        case "lblAnnouncement":
            show_announcements(cmfrm.FRAME, context.connection)
            return
        case "lblChoices":
            show_choice_manager(cmfrm.FRAME, context.connection, {
                "Priority", "Color", "AltColor", "ProjectCategory", "Status",
                "MarriageStatus", "UsedAs", "State", "Preacher", "Author",
                "DocumentType", "AttendanceType", "DateType", "ContactLabel",
                "Type", "Location", "PrayerCategory", "AnnouncementCategory",
                "AddressLabel", "Reading", "Season", "Category",
            })
            return
        case "lblSchedule":
            show_schedule_patterns(cmfrm.FRAME, context.connection)
            return
        case "lblGenerateOS":
            show_prepare_bulletin_order(cmfrm.FRAME, context.connection)
            return
        case "lblNotifyParticipants":
            frm = context.form_factory.create("frmNotifyviaeMail", ["Close"])
            frm.CONTROLID["btnNotify"].Bind(wx.EVT_LEFT_DOWN, _runNotify)
            frm.show()
            return
        case "lblSundayPrayers":
            _runSundayPrayers()
        case "lblAnnouncements":
            _runSundayAnnouncements()
        case "lblServiceSchedule":
            show_service_participants(cmfrm.FRAME, context.connection)
            return
        case "lblReports":
            frm = context.form_factory.create("frmReports", ["Close"])
            context.services.reports.configure_catalog_picker(frm.CONTROLID["ReportID"])
            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runReports)
            frm.disable_all_buttons()
            frm.enable_button("ChurchID")
            frm.enable_button("ReportID")
            frm.enable_button("btnRun")
            frm.enable_button("btnClose")
            frm.show()
            frm.CONTROLID["ReportID"].SetFocus()
            return
        case "lblReportDesigner":
            open_directory_designer(authorization=context.authorization)
            return
        case "lblScreenDesigner":
            open_churchmanager_screen_designer(
                context.connection, context.session, context.authorization,
                test_mode=context.test_mode,
            )
            return
        case "lblBackupDB":
            show_backup_restore(cmfrm.FRAME, context, JSForm)
            return
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
        case "lblAccountingGeneralLedger":
            show_general_ledger(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingFundBalances":
            show_fund_balances(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingReconciliationReport":
            show_reconciliation_report(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingCloseChecklist":
            show_close_checklist(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingBudgets":
            show_budgets(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingBudgetActual":
            show_budget_actual(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingFunctionalExpenses":
            show_functional_expenses(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case "lblAccountingYearEnd":
            show_year_end(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
        case _:
            raise KeyError("No ChurchManager menu route for {}".format(select))


def main(argv=None):
    global arguments, app, ChurchDB, cmfrm, context, single_instance
    from startup import build_runtime

    single_instance = ChurchManagerSingleInstance(Path(__file__).resolve().parent)
    if not single_instance.acquire():
        notice_app = wx.App(False)
        wx.MessageBox(
            "ChurchManager is already running. Close the existing ChurchManager window "
            "before starting another copy.",
            "ChurchManager Already Running",
            wx.OK | wx.ICON_INFORMATION,
        )
        notice_app.Destroy()
        return 1

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
        reports=ChurchManagerReportService(
            JSForm, processes,
            ReportAccessService(context.connection, context.authorization),
            connection_settings=context.settings,
        ),
    )

    closing = {"started": False}
    def on_main_close(event):
        if closing["started"]:
            event.Skip(); return
        closing["started"] = True
        if not getattr(context, "skip_auto_backup", False):
            try:
                run_automatic_exit_backup(context, JSForm)
            except Exception as error:
                wx.MessageBox(
                    "The automatic database backup could not be created.\n\n{}\n\n"
                    "ChurchManager will still close.".format(error),
                    "Automatic Backup Failed", wx.OK | wx.ICON_WARNING, cmfrm.FRAME,
                )
        event.Skip()
    cmfrm.FRAME.Bind(wx.EVT_CLOSE, on_main_close)

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
    restart = bool(getattr(context, "restart_requested", False))
    try:
        ChurchDB.DBConnection.close(); ChurchDB.JSConnection.close()
    except Exception:
        pass
    if restart:
        single_instance.release()
        command = [sys.executable, str(Path(__file__).resolve())]
        if context.test_mode:
            command.append("--test")
        subprocess.Popen(command)


if __name__ == "__main__":
    main()
