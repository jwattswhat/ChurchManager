import wx
import mysql
import mysql.connector

import clsForms
from clsFields import getcontrolparameters
import clsDB

#
# 	Main Program
#
app = wx.App(0)

#
# 	DataBase
#
ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
#
# 	Main form
#
frm = clsForms.clsForm(None, ChurchDBConnection, "frmAttendance", ["Navigation"])
frm.show()

app.MainLoop()
