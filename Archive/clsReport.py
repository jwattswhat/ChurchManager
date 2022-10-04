# !/usr/bin/env python3
# 	clsReport.py  Church Manager - Reports v0.1
#   Description <TODO>
#
# 	Rev. Jonathan C. Watt
# 	September 18, 2021


import wx
import mysql

import clsDB
import clsForms

from CMFormDescriptions import frmReportMainFORM, frmReportMainCONTROLS
from CMFormDescriptions import frmPropersDisplayFORM, frmPropersDisplayCONTROLS

#
# 	Classes
#


class MainForm(clsForms.clsForm):
    def edit_propers_display_click(self, event):
        """
        Church Add/Edit/Delete Form
        """

        if frmPropersDisplayFORM["name"] not in self.LINKEDFORM:
            PropersDisplayForm = clsForms.clsForm(
                self,
                self.DBConnection,
                frmPropersDisplayFORM,
                frmPropersDisplayCONTROLS,
            )
            self.LINKEDFORM.update({frmPropersDisplayFORM["name"]: PropersDisplayForm})
            PropersDisplayForm.show(True)

            # PropersDisplayForm.Bind(wx.EVT_BUTTON, self.edit_propers_display_click, self.CONTROLID["btnPropersDisplay"])
            PropersDisplayForm.FORM.Bind(
                wx.EVT_BUTTON,
                PropersDisplayForm.on_close_click,
                PropersDisplayForm.CONTROLID["btnClose"],
            )

    def bind_form_controls(self):
        self.FORM.Bind(
            wx.EVT_BUTTON,
            self.edit_propers_display_click,
            self.CONTROLID["btnPropersDisplay"],
        )
        self.FORM.Bind(wx.EVT_BUTTON, self.on_close_click, self.CONTROLID["btnClose"])

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
frmMainFORM = MainForm(
    None, ChurchDBConnection, frmReportMainFORM, frmReportMainCONTROLS
)
frmMainFORM.FORM.Centre()
frmMainFORM.show(True)

app.MainLoop()
