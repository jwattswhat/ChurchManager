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
from churchmanager_screen_designer import choice_eligible_fields, open_churchmanager_screen_designer
from user_admin import show_user_administration
from bulletin_order_dialog import show_bulletin_orders
from bulletin_order_generator_dialog import show_prepare_bulletin_order
from weekly_bulletin_order_dialog import show_weekly_bulletin_order
from worship_service_dialog import show_worship_services
from attendance_dialog import show_attendance
from worship_checklist import show_checklist_maintenance
from worship_scheduling import (
    show_participants, show_schedule_patterns, show_service_participants, show_worship_roles,
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
from churchmanager_error_support import (
    configure_churchmanager_error_reporting, show_support_diagnostics,
    update_runtime_context,
)
from participant_notification_dialog import show_participant_notifications
from mail_settings import show_mail_settings
from local_hymns import LocalHymnIDAllocator
from lectionary_package_dialog import show_lectionary_packages
from local_lectionary_dialog import show_local_lectionaries
from user_help import UserGuideError, open_user_guide
from giving.contributor_dialog import show_contributors
from giving.purpose_dialog import show_giving_purposes
from giving.batch_dialog import show_contribution_batches
from giving.report_dialog import show_giving_reports
from pastoral_care_dialog import show_pastoral_care
from group_dialog import show_groups
from group_meeting_dialog import show_group_attendance
from data_management import show_data_management
from custom_profile_dialog import show_custom_profile
from custom_profile_admin_dialog import show_custom_profile_administration
from custom_profile_search_dialog import show_custom_profile_search
from calendar_event_dialog import show_calendar_events
from calendar_integration_dialog import show_calendar_integration


arguments = None
app = None
ChurchDB = None
cmfrm = None
context = None
single_instance = None


class clsForm(JSForm.clsForm):
    def fill_form(self, record):
        """Fill a form and protect package-owned catalog controls."""
        for name in getattr(self, "_package_disabled_controls", set()):
            control = self.CONTROLID.get(name)
            if control:
                control.Enable(True)
        self._package_disabled_controls = set()
        result = super().fill_form(record)
        if self.FORMNAME == "frmHymn" and record:
            packaged = bool(record.get("PackageOwned")) or int(record.get("ID") or 0) >= 10001
            if "HymnalID" in self.CONTROLID:
                self.CONTROLID["HymnalID"].Disable()
            if "Hymn" in self.CONTROLID:
                self.CONTROLID["Hymn"].Enable(not packaged)
        if self.FORMNAME in {"frmLectionarySystem", "frmPropers"} and record:
            packaged = record.get("PackageID") is not None or bool(record.get("IsStarter"))
            if packaged:
                for name in record:
                    if name in {"ID", "PackageID", "IsStarter"}:
                        continue
                    control = self.CONTROLID.get(name)
                    if control and hasattr(control, "Enable"):
                        control.Enable(False)
                        self._package_disabled_controls.add(name)
        return result

    def new_record(self):
        """Create records, assigning permanent IDs to local hymns."""
        super().new_record()
        if self.FORMNAME != "frmHymn" or not self.RECORDS or not self.RECORDS.current():
            return
        if self.RECORDS.original.record.get("ID") is not None:
            return
        record = self.RECORDS.current()
        if record.get("ID") is None:
            hymn_id, entry_slot = LocalHymnIDAllocator(self.DBConnection).allocate()
            record["ID"] = hymn_id
            record["HymnalID"] = 1
            record["EntrySlot"] = entry_slot
            record["PackageOwned"] = 0
            record["IsActive"] = 1
            self.fill_form(record)

    def _on_update_record_click(self, event):
        """Synchronize local hymn identity metadata before the normal save."""
        if self._protected_lectionary_record():
            wx.MessageBox(
                "Packaged lectionary records are read-only. Install an updated package "
                "or create a local record instead.",
                "Protected Lectionary Record", wx.OK | wx.ICON_INFORMATION, self.FORM,
            )
            return
        if self.FORMNAME == "frmHymn" and self.RECORDS and self.RECORDS.current():
            record = self.RECORDS.current()
            if record.get("HymnalID") == 1 or 5001 <= int(record.get("ID") or 0) <= 9999:
                self.CONTROLID["HymnalID"].SetValue(1)
                record["HymnalID"] = 1
                record["PrintedReference"] = self.CONTROLID["Hymn"].GetValue().strip()
        super()._on_update_record_click(event)

    def _on_delete_record_click(self, event):
        """Retire hymn metadata instead of physically deleting permanent IDs."""
        if self._protected_lectionary_record():
            wx.MessageBox(
                "Packaged lectionary records cannot be deleted here. Retire the owning "
                "package from Lectionary Packages instead.",
                "Protected Lectionary Record", wx.OK | wx.ICON_INFORMATION, self.FORM,
            )
            return
        if self.FORMNAME != "frmHymn":
            return super()._on_delete_record_click(event)
        record = self.RECORDS.current() if self.RECORDS else None
        if not record or record.get("ID") is None:
            return
        if record.get("PackageOwned") or int(record["ID"]) >= 10001:
            wx.MessageBox(
                "Packaged hymns cannot be deleted. A package update may retire an entry.",
                "Protected Hymn", wx.OK | wx.ICON_INFORMATION, self.FORM,
            )
            return
        if wx.MessageBox(
            "Retire this local hymn? Its permanent ID will never be reused.",
            "Retire Hymn", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self.FORM,
        ) != wx.YES:
            return
        LocalHymnIDAllocator(self.DBConnection).retire(record["ID"])
        record["IsActive"] = 0
        self.RECORDS.original.saverecord(record)
        self.fill_form(record)

    def _protected_lectionary_record(self):
        """Return true when the current form row belongs to an installed package."""
        if self.FORMNAME not in {"frmLectionarySystem", "frmPropers"}:
            return False
        record = self.RECORDS.current() if self.RECORDS else None
        return bool(record and (
            record.get("PackageID") is not None or record.get("IsStarter")
        ))

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
        if "btnAdditionalInformation" in self.CONTROLID:
            self.CONTROLID["btnAdditionalInformation"].Bind(
                wx.EVT_BUTTON, self._open_additional_information,
            )
        super().bind_form_controls()

    def _open_additional_information(self, _event):
        """Open dynamic profile data for the current saved Person or Family."""
        record = self.RECORDS.current() if self.RECORDS else None
        entity_type = "PERSON" if self.FORMNAME == "frmPerson" else "FAMILY"
        if not record or not record.get("ID") or not record.get("ChurchID"):
            wx.MessageBox(
                "Save this profile before adding church-defined information.",
                "Additional Information", wx.OK | wx.ICON_INFORMATION, self.FORM,
            )
            return
        label = (
            " ".join(filter(None, (record.get("FirstName"), record.get("LastName"))))
            if entity_type == "PERSON" else record.get("FamilyName")
        ) or entity_type.title()
        try:
            show_custom_profile(
                self.FORM, self.DBConnection, context.session, self.AUTHORIZATION_POLICY,
                record["ChurchID"], entity_type, record["ID"], label,
            )
        except (PermissionError, ValueError) as error:
            wx.MessageBox(str(error), "Additional Information Unavailable", wx.OK | wx.ICON_ERROR, self.FORM)

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
    if select == "lblHelp":
        try:
            open_user_guide()
        except UserGuideError as error:
            wx.MessageBox(str(error), "User Guide", wx.OK | wx.ICON_ERROR, cmfrm.FRAME)
        return
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
        case "lblWorshipPositions":
            show_worship_roles(cmfrm.FRAME, context.connection)
            return
        case "lblPrayers":
            show_prayers(cmfrm.FRAME, context.connection, context.session, context.authorization)
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
            }, choice_eligible_fields())
            return
        case "lblSchedule":
            show_schedule_patterns(cmfrm.FRAME, context.connection)
            return
        case "lblGenerateOS":
            show_prepare_bulletin_order(cmfrm.FRAME, context.connection)
            return
        case "lblNotifyParticipants":
            show_participant_notifications(
                cmfrm.FRAME, context.connection, context.authorization,
                context.services.reports, context.services.processes,
                test_mode=context.test_mode,
            )
            return
        case "lblSundayPrayers":
            _runSundayPrayers()
        case "lblAnnouncements":
            _runSundayAnnouncements()
        case "lblServiceSchedule":
            show_service_participants(cmfrm.FRAME, context.connection)
            return
        case "lblAttendanceEvent" | "lblRecordAttendance":
            show_attendance(cmfrm.FRAME, context.connection, context.authorization, context.session)
            return
        case "lblReports":
            frm = context.form_factory.create("frmReports", ["Close"])
            context.services.reports.configure_catalog_picker(frm.CONTROLID["ReportID"])
            context.services.reports.configure_group_picker(frm.CONTROLID["GroupID"])
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
        case "lblEmailSettings":
            show_mail_settings(cmfrm.FRAME, context.connection, context.authorization, context.test_mode)
            return
        case "lblSupportDiagnostics":
            show_support_diagnostics(cmfrm.FRAME)
            return
        case "lblLectionaryPackages":
            show_lectionary_packages(
                cmfrm.FRAME, context.connection, context.authorization,
            )
            return
        case "lblGivingContributors":
            show_contributors(
                cmfrm.FRAME, context.connection, context.session, context.authorization
            )
            return
        case "lblGivingPurposes":
            show_giving_purposes(cmfrm.FRAME, context.connection, context.authorization)
            return
        case "lblContributionBatches":
            show_contribution_batches(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
                context.test_mode,
            )
            return
        case "lblGivingReports":
            show_giving_reports(
                cmfrm.FRAME, context.connection, context.authorization, context.session
            )
            return
        case "lblPastoralCare":
            show_pastoral_care(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
                context.services.pastoral_cipher,
            )
            return
        case "lblGroups":
            show_groups(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
                test_mode=context.test_mode,
            )
            return
        case "lblGroupAttendance":
            show_group_attendance(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
            )
            return
        case "lblDataManagement":
            show_data_management(cmfrm.FRAME, context.connection, context.session)
            return
        case "lblCustomProfileFields":
            show_custom_profile_administration(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
            )
            return
        case "lblCustomProfileSearch":
            show_custom_profile_search(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
            )
            return
        case "lblCalendarEvents":
            show_calendar_events(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
            )
            return
        case "lblCalendarIntegration":
            show_calendar_integration(cmfrm.FRAME, context.connection, context.authorization)
            return
        case "lblPropers":
            show_local_lectionaries(
                cmfrm.FRAME, context.connection, context.authorization,
            )
            return
        case "lblUsers":
            show_user_administration(
                cmfrm.FRAME, context.connection, context.session, context.authorization,
                minimum_length=4 if context.test_mode else 12,
                test_mode=context.test_mode,
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
    configure_churchmanager_error_reporting()
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
    update_runtime_context(arguments, runtime.session)
    context.form_factory = ChurchManagerFormFactory(
        clsForm, context.connection, cmfrm,
        authorization_policy=context.authorization,
    )
    processes = ProcessService()
    from pastoral_note_crypto import PastoralKeyManager, PastoralNoteCipher, PastoralRecoveryBackup
    recovery_root = Path(os.environ.get("LOCALAPPDATA", Path.cwd())) / "ChurchManager"
    recovery = PastoralRecoveryBackup(
        PastoralKeyManager(
            JSForm.WindowsCredentialStore(),
            "ChurchManager/{}/PastoralNotes".format(context.settings["database"]),
        ),
        recovery_root / "pastoral-recovery.{}.json".format(
            context.settings["database"]
        ),
    )
    context.services = SimpleNamespace(
        processes=processes,
        backups=BackupService(recovery=recovery),
        pastoral_cipher=PastoralNoteCipher(recovery.key_manager),
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
