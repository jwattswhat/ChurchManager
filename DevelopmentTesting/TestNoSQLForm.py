import wx
import mysql
import clsDB
import clsFields
import clsConfig
from clsForms import clsNoSQLForm
from clsConfig import CONFIG

#
# 	Main Program
#
app = wx.App(0)
#
# 	Connect to DataBase
#
#
# 	Main form
#

ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
CONFIG.set_Config_DBConnection(ChurchDBConnection)

record = [{"Name":"Jonathan C. Watt"},{"Name":"Paul Johnson"}]

frm = clsNoSQLForm(None, ChurchDBConnection,"frmTestNoSQL", ["Close"])
#
# bind application events
#

frm.show()
frm.display_form_data(frm.FORMDESCRIPTON,record)
app.MainLoop()
print(frm.get_record())



