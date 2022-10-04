import wx

import mysql
import mysql.connector
import clsDB
import clsFont


#
# 	Main Program
#
app = wx.App(0)

#
# 	DataBase
#
ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
frm = wx.Frame(None,wx.ID_ANY)
myfont = clsFont.clsFont(ChurchDBConnection)
myfont.Get_Config_Font()
myfont.Font_Dialog(frm)
myfont.Set_Config_Font()
app.MainLoop()
