import wx
import mysql.connector

from clsConfig import CONFIG
import clsDB
from clsError import ErrorHandler
import clsForms


def _buttonclick(event):
    form = frm.CONTROLID["Forms"].GetValueText()
    btn = event.GetEventObject().GetName()
    form = clsForms.clsForm(None, ChurchDBConnection, form, ["Navigation", "Close"])
    form.display_form_data()
    form.show()


#
# 	Main Program
#
app = wx.App(0)
#
# 	Connect to DataBase
#
ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
CONFIG.set_Config_DBConnection(ChurchDBConnection)
#
# 	Main form
#
frm = clsForms.clsForm(None, ChurchDBConnection, "frmOpenMembership", ["Close"])

#
# bind application events
#

frm.FORM.Bind(wx.EVT_BUTTON, _buttonclick, frm.CONTROLID["btnOpen"])

frm.show()
frm.display_form_data()
app.MainLoop()
