# !/usr/bin/env python3
# 	CMutility.py  Church Manager - Utility v0.1
#   Description <TODO>
#
# 	Rev. Jonathan C. Watt
# 	July 1, 2021

import wx
import mysql

import clsFont
import clsDB
import clsForms

#
# 	Classes
#


class MainForm(clsForms.clsForm):
    def edit_font_click(self, event):
        self.font = clsFont.clsFont(self.DBConnection)
        self.font.Get_Config_Font()
        self.font.Font_Dialog(self.FORM)
        self.font.Set_Config_Font()

    def bind_form_controls(self):
        self.FORM.Bind(
            wx.EVT_BUTTON, self.edit_font_click, self.CONTROLID["btnEditFont"]
        )

        ##########################
        # Warning! leave in place
        # ########################
        super().bind_form_controls()


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
frmMainFORM = MainForm(None, ChurchDBConnection, "frmUtility", ["Close"])
frmMainFORM.FORM.Centre()
frmMainFORM.show()

app.MainLoop()
