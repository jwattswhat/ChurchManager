# 	CMw.py  Church Manager - Membership v0.1
#   Description <TODO> add description
# 	Rev. Jonathan C. Watt
# 	July 1, 2021

import wx
import mysql

import clsDB
import clsForms
from clsFields import getcontrolparameters


#
# 	Classes
#

#
# 	Main Program
#
app = wx.App(0)

#
# 	Open the DataBase
#
ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
#
# 	Main form
#
MainFORM = clsForms.clsForm(None, ChurchDBConnection, "frmMembershipMain", ["Close"])
MainFORM.FORM.Centre()
MainFORM.show()

app.MainLoop()
