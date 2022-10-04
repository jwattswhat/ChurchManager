"""
    cm.py - Church Manager.
    Rev. Jonathan C. Watt
    Copyright: 2022, Jonathan C. Watt
    
"""
import wx
import mysql
import subprocess

from clsMonitor import clsMonitor

from clsMonitor import PMON
from clsConstants import CONST
from clsConfig import CONFIG
from clsOption import OPTION
from clsFont import FONT
import clsDB
import clsSQL
import clsForms
import fnSchedule
import fnUtil
from clsSMTP import clsSMTP


def _buttonclick(event):
    def _runSPrpt(event):
        ID = frm.CONTROLID["ServiceID"].GetValue()
        if ID == None:
            return
        cmdline = "python rptWorshipPlanningWorksheet.py -I={ID}".format(ID=ID)
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
            frm = clsForms.clsForm(
                None, ChurchDBConnection, "frmGenerateWorshipPlanning", ["Close"]
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
            frm = clsForms.clsForm(None, ChurchDBConnection, "frmGenerateOS", ["Close"])

            frm.CONTROLID["btnRun"].Bind(wx.EVT_LEFT_DOWN, _runOSrpt)
            frm.display_form_data()
            frm.show()
            return
        case "lblNotifyParticipants":
            frm = clsForms.clsForm(None, ChurchDBConnection, "frmNotifyviaeMail")
            frm.CONTROLID["btnNotify"].Bind(wx.EVT_LEFT_DOWN, _runNotify)
            frm.display_form_data()
            frm.show()
            return

        case "lblSundayPrayers":
            subprocess.Popen("python rptPrayers.py", shell=True)

        case "lblMemberDirectory":
            subprocess.Popen("python rptMemberDirectory.py", shell=True)

        case "lblServiceSchedule":
            frm = clsForms.clsForm(
                None, ChurchDBConnection, "frmServiceSchedule", ["Navigation", "Close"]
            )
            frm.CONTROLID["btnRunSchedule"].Bind(wx.EVT_LEFT_DOWN, _runSchedule)
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
        case _:
            print("form name not found found. {}".format(formname))

    if formname != None:
        form = clsForms.clsForm(None, ChurchDBConnection, formname)
        form.display_form_data()
        form.show()


app = wx.App(0)
#
# 	Connect to DataBase
#

ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
CONFIG.set_Config_DBConnection(ChurchDBConnection)
OPTION.set_Option_DBConnection(ChurchDBConnection)
FONT.set_Font_DBConnection(ChurchDBConnection)
FONT.Get_Config_Font()
CONST.btnNavigationCONTROLS = fnUtil.convertNavButtions(CONST.btnNavigationCONTROLS)
#
# 	Main form
#
frm = clsForms.clsForm(None, ChurchDBConnection, "frmMain", ["Close"])

frm.CONTROLID["lblChurch"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblService"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblSermon"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblPropers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblWorshipPlan"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblOSList"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblOS"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblGenerateOS"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblNotifyParticipants"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblSundayPrayers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblPrayers"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblMemberDirectory"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblParticipant"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblSchedule"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblServiceSchedule"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblFamily"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblPeople"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

frm.CONTROLID["lblConfig"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblOptions"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblChoices"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)
frm.CONTROLID["lblBugs"].Bind(wx.EVT_LEFT_DOWN, _buttonclick)

PARENTRECORD = {}
#
# bind application events
#

frm.show()
frm.display_form_data()
app.MainLoop()
