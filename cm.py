"""
    cm.py - Church Manager
    Rev. Jonathan C. Watt
    Copyright: 2022, Jonathan C. Watt
    July 2022
    
"""
import os
import wx
import mysql
import subprocess
import json
import argparse

import JSForm
import fnSchedule


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
        JSForm.RunReport(2, frm, ChurchDB.DBConnection)

    def _runOSrpt(event):
        ID = frm.CONTROLID["ServiceID"].GetValue()
        if ID == None:
            return
        cmdline = "python rptOrderofService.py -I={ID}".format(ID=ID)
        subprocess.Popen(cmdline, shell=True)
        frm.FORM.Close()

    def _runSchedule(event):
        ID = int(frm.CONTROLID["ServiceID"].GetValue())
        if ID == None:
            return
        fnSchedule.ScheduleParticipants(ID)

    def _runNotify(event):
        ID = int(frm.CONTROLID["ServiceID"].GetValue())
        if ID == None:
            return
        fnSchedule.notifyviaeMail(ID)
        frm.FORM.Close()

    def _runPrayerRequests():
        reportdescription = JSForm.CONFIG.get_Config_Value(
            "Location", "ReportDescription"
        )
        report = JSForm.CONFIG.get_Config_Value("Location", "Report")
        limedir = JSForm.CONFIG.get_Config_Value("Location", "LimeReport")
        try:
            os.remove("{report}CMPR01.pdf".format(report=report))
        except:
            pass
        cmdline = "{limedir}limereport -s{reportdescription}CMPR01.lrxml -d{report}CMPR01.pdf".format(
            limedir=limedir, reportdescription=reportdescription, report=report
        )
        sb = subprocess.Popen(cmdline)
        sb.wait()
        cmdline = "{report}CMPR01.pdf".format(report=report)
        sb = subprocess.Popen(cmdline, shell=True)

    def _runSundayPrayers():
        sb = subprocess.Popen("python rptPrayers.py", shell=True)

    def _runSundayAnnouncements():
        sb = subprocess.Popen("python rptAnnouncement.py")

    def _runReports(event):
        reportid = frm.CONTROLID["ReportID"].GetValue()
        JSForm.RunReport(reportid, frm, ChurchDB.DBConnection)
        frm.FORM.Close()

    select = event.GetEventObject().GetName()
    formname = None
    match select:
        case "lblChurch":
            formname = "frmChurch"
        case "lblService":
            formname = "frmService"
        case "lblSermon":
            formname = "frmSermon"
        case "lblPropers":
            formname = "frmPropers"
        case "lblWorshipPlan":
            frm = (
                cmfrm,
                ChurchDB.DBConnection,
                "frmGenerateWorshipPlanning",
                ["Close"],
            )
            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runSPrpt)
            frm.show()
            return
        case "lblPrayers":
            formname = "frmPrayer"
        case "lblOSList":
            formname = "frmOSList"
        case "lblOS":
            formname = "frmOS"
        case "lblCheckList":
            formname = "frmCheckList"
        case "lblGenerateOS":
            frm = clsForm(cmfrm, ChurchDB.DBConnection, "frmGenerateOS", ["Close"])

            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runOSrpt)
            frm.show()
            return
        case "lblNotifyParticipants":
            frm = clsForm(cmfrm, ChurchDB.DBConnection, "frmNotifyviaeMail")
            frm.CONTROLID["btnNotify"].Bind(wx.EVT_LEFT_DOWN, _runNotify)
            frm.show()
            return
        case "lblSundayPrayers":
            _runSundayPrayers()
        case "lblAnnouncements":
            _runSundayAnnouncements()
        case "lblPrayerRequests":
            _runPrayerRequests()
        case "lblMemberDirectory":
            subprocess.Popen("python rptMemberDirectory.py", shell=True)
        case "lblServiceSchedule":
            frm = clsForm(
                cmfrm,
                ChurchDB.DBConnection,
                "frmServiceSchedule",
                ["Navigation", "Close"],
            )
            frm.CONTROLID["btnRunSchedule"].Bind(wx.EVT_LEFT_DOWN, _runSchedule)
            frm.show()
            return
        case "lblReports":
            frm = clsForm(cmfrm, ChurchDB.DBConnection, "frmReports", ["Close"])
            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runReports)
            frm.disable_all_buttons()
            frm.enable_button("ReportID")
            frm.enable_button("btnRun")
            frm.enable_button("btnClose")
            frm.show()
            return
        case "lblEnhancements":
            formname = "frmEnhancement"
        case "lblFamily":
            formname = "frmFamily"
        case "lblPerson":
            formname = "frmPerson"
        case "lblAttendanceEvent":
            formname = "frmAttendanceEvent"
        case "lblRecordAttendance":
            formname = "frmRecordAttendance"

        case "lblParticipant":
            formname = "frmParticipant"
        case "lblSchedule":
            formname = "frmSchedule"
        case "lblConfig":
            formname = "frmConfig"
        case "lblOptions":
            formname = "frmOptions"
        case "lblChoices":
            formname = "frmChoices"
        case "lblProject":
            formname = "frmProject"
        case "lblTask":
            formname = "frmTask"
        case "lblDonor":
            formname = "frmDonor"
        case "lblDonorGift":
            formname = "frmDonorGift"
        case _:
            print("form name not found found. {}".format(formname))

    if formname != None:
        form = clsForm(cmfrm, ChurchDB.DBConnection, formname)
        form.show()


cmparser = argparse.ArgumentParser(
    prog="ChurchManager", description="Church Manager v0.1"
)
cmparser.add_argument("-s", "--server", type=str, default="localhost")
cmparser.add_argument("-d", "--database", type=str, default="ChurchDB")
cmparser.add_argument("-u", "--user", type=str)
cmparser.add_argument("-p", "--password", type=str)

args = cmparser.parse_args()
# print(args.server,args.database,args.user,args.password)


server = args.server
database = args.database
user = args.user
password = args.password

app = wx.App(0)

#
# 	Connect to DataBase
#
JSFormDB = JSForm.clsDB(databasename="JSForm", username="church", password="Church99")
JSForm.JSFORMCONFIG.set_Config_DBConnection(JSFormDB.DBConnection)
ChurchDB = JSForm.clsDB(server, database, user, password)
JSForm.CONFIG.set_Config_DBConnection(ChurchDB.DBConnection)
JSForm.OPTION.set_Option_DBConnection(ChurchDB.DBConnection)
JSForm.FONT.set_Font_DBConnection(ChurchDB.DBConnection)
JSForm.FONT.Get_Config_Font()
JSForm.CONST.btnNavigationCONTROLS = JSForm.convertNavButtons(
    JSForm.CONST.btnNavigationCONTROLS
)

#
# 	Main form
#
cmfrm = clsForm(None, ChurchDB.DBConnection, "frmMain", ["Close"])

#
# bind application events
#
cmfrm.CONTROLID["lblChurch"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblService"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblSermon"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblPropers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblOSList"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblOS"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblCheckList"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblGenerateOS"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblNotifyParticipants"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblSundayPrayers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblPrayers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblReports"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblAnnouncements"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblEnhancements"].Bind(wx.EVT_LEFT_DOWN,_buttonclick)

cmfrm.CONTROLID["lblParticipant"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblSchedule"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblServiceSchedule"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblFamily"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblPerson"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblAttendanceEvent"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblConfig"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblOptions"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblChoices"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblProject"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblTask"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblDonor"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblDonorGift"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblRecordAttendance"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

PARENTRECORD = {}
cmfrm.show()
app.MainLoop()
