# !/usr/bin/env python3
# 	CMattendance.py  Church Manager - Project v0.1
#   Description <TODO> add description
# 	Rev. Jonathan C. Watt
# 	July 1, 2021

import wx
import mysql

import clsDB
import clsForms
from CMFormDescriptions import frmAttendanceMainFORM, frmAttendanceMainCONTROLS
from CMFormDescriptions import frmChurchFORM, frmChurchCONTROLS

from CMFormDescriptions import frmPersonFORM, frmPersonCONTROLS
from CMFormDescriptions import frmServiceFORM, frmServiceCONTROLS

from CMFormDescriptions import frmAttendanceFORM, frmAttendanceCONTROLS

# from CMFormDescriptions import frmAttendanceTypeFORM, frmAttendanceTypeCONTROLS
# from CMFormDescriptions import frmAttendanceEventFORM, frmAttendanceEventCONTROLS

#
# 	Classes
#


class MainForm(clsForms.clsForm):
    # <TODO> close all LINKEDFORMs on close of main form
    def edit_church_click(self, event):
        #
        # 	Church Add/Edit/Delete
        #
        if frmChurchFORM["name"] not in self.LINKEDFORM.keys():
            ChurchForm = clsForms.clsRecordForm(
                self, self.DBConnection, frmChurchFORM, frmChurchCONTROLS
            )
            self.LINKEDFORM.update({frmChurchFORM["name"]: ChurchForm})
            ChurchForm.show(True)

    def edit_person_click(self, event):
        #
        #   Person Add/Edit/Delete
        #
        if frmPersonFORM["name"] not in self.LINKEDFORM.keys():
            PersonForm = clsForms.clsRecordForm(
                self, self.DBConnection, frmPersonFORM, frmPersonCONTROLS
            )
            self.LINKEDFORM.update({frmPersonFORM["name"]: PersonForm})
            PersonForm.show(True)

    def edit_service_click(self, event):
        #
        #   Person Add/Edit/Delete
        #
        if frmServiceFORM["name"] not in self.LINKEDFORM.keys():
            ServiceForm = clsForms.clsRecordForm(
                self, self.DBConnection, frmServiceFORM, frmServiceCONTROLS
            )
            self.LINKEDFORM.update({frmServiceFORM["name"]: ServiceForm})
            ServiceForm.show(True)

    def edit_attendance_click(self, event):
        #
        #   Attendance Add/Edit/Delete
        #
        if frmAttendanceFORM["name"] not in self.LINKEDFORM.keys():
            AttendanceForm = clsForms.clsRecordForm(
                self, self.DBConnection, frmAttendanceFORM, frmAttendanceCONTROLS
            )
            self.LINKEDFORM.update({frmAttendanceFORM["name"]: AttendanceForm})
            AttendanceForm.show(True)

    def bind_form_controls(self):
        self.FORM.Bind(
            wx.EVT_BUTTON, self.edit_church_click, self.CONTROLID["btnEditChurch"]
        )
        self.FORM.Bind(
            wx.EVT_BUTTON, self.edit_person_click, self.CONTROLID["btnEditPerson"]
        )
        self.FORM.Bind(
            wx.EVT_BUTTON, self.edit_service_click, self.CONTROLID["btnEditService"]
        )
        self.FORM.Bind(
            wx.EVT_BUTTON,
            self.edit_attendance_click,
            self.CONTROLID["btnEditAttendance"],
        )
        self.FORM.Bind(wx.EVT_BUTTON, self.on_close_click, self.CONTROLID["btnClose"])

        ##########################
        # Warning! leave in place
        # ########################
        clsForms.clsForm.bind_form_controls(self)


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
frmMainFORM = MainForm(
    None, ChurchDBConnection, frmAttendanceMainFORM, frmAttendanceMainCONTROLS
)
frmMainFORM.FORM.Centre()
frmMainFORM.show(True)

app.MainLoop()
