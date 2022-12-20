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
    class MergeorReplaceChecklist(wx.Dialog):
        def __init__(self, parent, title):
            super().__init__(parent, title=title, size=(400, 200))
            panel = wx.Panel(self)
            self.text = wx.StaticText(
                panel,
                wx.ID_ANY,
                label="Merge or Replace this CheckList with existing?",
                pos=(10, 50),
            )
            self.btn = wx.Button(
                panel, wx.ID_OK, label="Merge", size=(100, 30), pos=(10, 100)
            )
            self.btn = wx.Button(
                panel, wx.ID_CANCEL, label="Replace", size=(100, 30), pos=(120, 100)
            )

    def bind_form_controls(self):
        JSForm.LG.log()
        if "CheckListID" in self.CONTROLID:
            self.CONTROLID["CheckListID"].Bind(wx.EVT_TEXT, self._fillchecklist)
            self.CONTROLID["CheckList"].Bind(
                wx.EVT_CHECKLISTBOX, self._checkboxallchecked
            )
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

    def _fillchecklist(self, event):
        field = event.GetEventObject().GetName()
        evnttype = event.GetEventType()
        ID = self.CONTROLID[field].GetValue()
        if ID is None:
            return None
        sql = "SELECT CheckList FROM tblCheckList WHERE ID = {ID};".format(ID=ID)
        cursor = self.DBConnection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        newchecklist = json.loads(row[0])
        fld = self.CONTROLID["CheckList"].GetValue()
        if fld != None:
            existingchecklist = json.loads(fld)
            if len(existingchecklist) == 0:
                self.CONTROLID["CheckList"].SetValue(json.dumps(newchecklist))
                self.CONTROLID["CheckListComplete"].SetValue(False)
                return
        dlg = self.MergeorReplaceChecklist(self.FORM, title="CheckList Merge / Replace")
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:  # ok is merge
            self.CONTROLID["CheckList"].SetValue(
                json.dumps(newchecklist | existingchecklist)
            )
        else:  # cancel is replace
            self.CONTROLID["CheckList"].SetValue(json.dumps(newchecklist))
        self.CONTROLID["CheckListComplete"].SetValue(False)

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

    def _addIDtofilename(self,event):
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
            newfilename = filename[0]+".ID("+str(ID)+")"+filename[1]
            os.rename(
                filename[0]+filename[1],newfilename)
            self.CONTROLID[field].SetValue(newfilename)

def _buttonclick(event):
    def _runSPrpt(event):
        reportdescription = JSForm.CONFIG.get_Config_Value(
            "Location", "ReportDescription"
        )
        report = JSForm.CONFIG.get_Config_Value("Location", "Report")
        limedir = JSForm.CONFIG.get_Config_Value("Location", "LimeReport")
        ID = frm.CONTROLID["ServiceID"].GetValue()
        if ID == None:
            return
        try:
            os.remove("{report}CMWP01.pdf".format(report=report))
        except:
            pass
        cmdline = "{limedir}limereport -s{reportdescription}CMWP01.lrxml -d{report}CMWP01.pdf -pserviceid={ID}".format(
            limedir=limedir, reportdescription=reportdescription, report=report, ID=ID
        )
        sb = subprocess.Popen(cmdline)
        sb.wait()
        cmdline = "{report}CMWP01.pdf".format(report=report)
        subprocess.Popen(cmdline, shell=True)
        frm.FORM.Close()

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
        class _requiredfielddialog(wx.Dialog):
            def __init__(self, parent, title, report="", field=""):
                super().__init__(parent, title=title, size=(400, 200))
                panel = wx.Panel(self)
                self.text = wx.StaticText(
                    panel,
                    wx.ID_ANY,
                    label="Field {field} Required for FORM {report}.".format(field=field,report=report),
                    pos=(10, 50),
                )
                self.btn = wx.Button(
                    panel,
                    JSForm.CONST.FORM_CONTINUE,
                    label="Continue",
                    size=(100, 30),
                    pos=(10, 100),
                )

        reportpattern = JSForm.CONFIG.get_Config_Value(
            "Location", "LimeReportPattern"
        )
        reportlocation = JSForm.CONFIG.get_Config_Value("Location", "Report")
        limedir = JSForm.CONFIG.get_Config_Value("Location", "LimeReport")

        ReportID = frm.CONTROLID["ReportID"].GetValue()
        if ReportID == None:
            dlg = _requiredfielddialog(frm.FORM,"Report Selection Required")
            result = dlg.ShowModal()
            dlg.Destroy()
            return None

        SQL = "SELECT * FROM tblReports WHERE ID = {ID};".format(ID=ReportID)
        cursor = ChurchDB.DBConnection.cursor()
        cursor.execute(SQL)
        row = cursor.fetchone()
        cursor.close()
        if row == None:
            dlg = _requiredfielddialog(frm.FORM,"Report Not Found",rptTitle,"Report")
            result = dlg.ShowModal()
            dlg.Destroy()
            return None

        #   Name the record values
        rptReport = row[1]
        rptTitle = row[2]
        rptParams = row[3].replace("[", "")
        rptParams = rptParams.replace("]", "")
        rptParams = rptParams.replace(",", "")
        rptParams = rptParams.splitlines()
        rptNote = row[4]

        try:
            # Get Name from Report Record
            os.remove(
                "{reportlocation}{rptreport}.pdf".format(
                    report=reportlocation, rptreport=rptReport
                )
            )
        except:
            pass

        ChurchID = frm.CONTROLID["ChurchID"].GetValue()
        if "ChurchID" in rptParams and ChurchID == None:
            dlg = _requiredfielddialog(frm.FORM,"Required Field",rptTitle,"Church")
            result = dlg.ShowModal()
            dlg.Destroy()
            return None

        ServiceID = frm.CONTROLID["ServiceID"].GetValue()
        if "ServiceID" in rptParams and ServiceID == None:
            dlg = _requiredfielddialog(frm.FORM,"Required Field",rptTitle,"Service")
            result = dlg.ShowModal()
            dlg.Destroy()
            return None

        cmdline = "{limedir}limereport -s{reportpattern}{rptreport}.lrxml -d{reportlocation}{rptreport}.pdf".format(
            limedir=limedir,
            reportpattern=reportpattern,
            reportlocation=reportlocation,
            rptreport=rptReport,
        )

        #   Replace with a mord generic form that uses rptParams to select from
        #   from andy table.
        if "ChurchID" in rptParams:
            cmdline = cmdline + " -pchurchid={churchid}".format(churchid=ChurchID)
        if "ServiceID" in rptParams:
            cmdline = cmdline + " -pserviceid={serviceid}".format(serviceid=ServiceID)

        sb = subprocess.Popen(cmdline)
        sb.wait()
        cmdline = "{reportlocation}{rptreport}.pdf".format(
            reportlocation=reportlocation, rptreport=rptReport
        )
        subprocess.Popen(cmdline, shell=True)
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
            frm = JSForm.clsForm(
                None, ChurchDB.DBConnection, "frmGenerateWorshipPlanning", ["Close"]
            )
            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runSPrpt)
            frm.display_form_data()
            frm.show()
            return
        case "lblPrayers":
            formname = "frmPrayer"
        case "lblOSList":
            formname = "frmOSList"
        case "lblOS":
            formname = "frmOS"
        case "lblGenerateOS":
            frm = JSForm.clsForm(
                None, ChurchDB.DBConnection, "frmGenerateOS", ["Close"]
            )

            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runOSrpt)
            frm.display_form_data()
            frm.show()
            return
        case "lblNotifyParticipants":
            frm = JSForm.clsForm(None, ChurchDB.DBConnection, "frmNotifyviaeMail")
            frm.CONTROLID["btnNotify"].Bind(wx.EVT_LEFT_DOWN, _runNotify)
            frm.display_form_data()
            frm.show()
            return
        case "lblSundayPrayers":
            _runSundayPrayers()
        case "lblPrayerRequests":
            _runPrayerRequests()
        case "lblMemberDirectory":
            subprocess.Popen("python rptMemberDirectory.py", shell=True)
        case "lblServiceSchedule":
            frm = JSForm.clsForm(
                None,
                ChurchDB.DBConnection,
                "frmServiceSchedule",
                ["Navigation", "Close"],
            )
            frm.CONTROLID["btnRunSchedule"].Bind(wx.EVT_LEFT_DOWN, _runSchedule)
            frm.display_form_data()
            frm.show()
            return
        case "lblReports":
            frm = JSForm.clsForm(None, ChurchDB.DBConnection, "frmReports", ["Close"])

            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runReports)
            frm.display_form_data()
            frm.show()
            return
        case "lblFamily":
            formname = "frmFamily"
        case "lblPeople":
            formname = "frmPerson"
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
        form = clsForm(None, ChurchDB.DBConnection, formname)
        form.display_form_data()
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
frm = clsForm(None, ChurchDB.DBConnection, "frmMain", ["Close"])

frm.CONTROLID["lblChurch"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblService"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblSermon"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblPropers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblOSList"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblOS"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblGenerateOS"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblNotifyParticipants"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblSundayPrayers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblPrayers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblReports"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblParticipant"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblSchedule"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblServiceSchedule"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblFamily"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblPeople"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblConfig"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblOptions"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblChoices"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblBugs"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblProject"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblTask"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

PARENTRECORD = {}
#
# bind application events
#

frm.show()
frm.display_form_data()
app.MainLoop()
