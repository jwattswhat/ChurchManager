import wx
import mysql
import mysql.connector

import clsForms
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
frm = clsForms.clsForm(None, ChurchDBConnection, "frmPersonDateGrid", ["Navigation"])
frm.FORM.Show(True)

app.MainLoop()
