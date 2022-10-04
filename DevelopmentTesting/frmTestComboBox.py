# !/usr/bin/env python3
from tabnanny import check
import wx
import wx.adv
import wx.richtext
import mysql
import mysql.connector

import clsBASEForms
from clsFields import getcontrolparameters
import clsDB

class clsForm(clsBASEForms.clsBASEForm):
    pass

# todo: close forms when master is closed.
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
frm = clsForm(None, ChurchDBConnection, "frmTestComboBox", ["Navigation","Close"])

#
# bind application events
#

frm.show()
app.MainLoop()
