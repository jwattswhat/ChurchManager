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

import JSForm
import fnSchedule


class clsForm(JSForm.clsForms.clsForm):
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
            frm.show()
            return
        case "lblFamily":
            formname = "frmFamily"
        case "lblPeople":
            formname = "frmPerson"
        case "lblAttendanceEvent":
            formname = "frmAttendanceEvent"
        case "lblAttendance":
            formname = "frmAttendance"
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
        case "lblBugs":
            formname = "frmBugs"
        case "lblProject":
            formname = "frmProject"
        case "lblTask":
            formname = "frmTask"
        case _:
            print("form name not found found. {}".format(formname))

    if formname != None:
        form = clsForm(cmfrm, ChurchDB.DBConnection, formname)
        form.show()


app = wx.App(0)

#
# 	Connect to DataBase
#
ChurchDB = JSForm.clsDB("localhost", "ChurchDB", "church", "Church99")
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

cmfrm.CONTROLID["lblParticipant"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblSchedule"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblServiceSchedule"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblFamily"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblPeople"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblAttendanceEvent"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblAttendance"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblConfig"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblOptions"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblChoices"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblBugs"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

cmfrm.CONTROLID["lblProject"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
cmfrm.CONTROLID["lblTask"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

PARENTRECORD = {}

cmfrm.show()
app.MainLoop()
