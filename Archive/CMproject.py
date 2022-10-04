# !/usr/bin/env python3
# 	CMproject.py  Church Manager - Project v0.1
#   Description <TODO> add description
# 	Rev. Jonathan C. Watt
# 	July 1, 2021

import wx
import mysql

import clsDB
import clsForms
from CMFormDescriptions import frmProjectMainFORM, frmProjectMainCONTROLS
from CMFormDescriptions import frmChurchFORM, frmChurchCONTROLS

from CMFormDescriptions import frmPersonFORM, frmPersonCONTROLS

from CMFormDescriptions import frmSkillFORM, frmSkillCONTROLS

from CMFormDescriptions import frmProjectFORM, frmProjectCONTROLS
from CMFormDescriptions import frmProjectTaskFORM, frmProjectTaskCONTROLS
from CMFormDescriptions import frmProjectSkillFORM, frmProjectSkillCONTROLS

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
            ChurchForm = clsForms.clsRecordForm(self, self.DBConnection, frmChurchFORM, frmChurchCONTROLS)
            self.LINKEDFORM.update({frmChurchFORM["name"]: ChurchForm})
            ChurchForm.show(True)

    def edit_person_click(self, event):
        #
        #   Person Add/Edit/Delete
        #
        if frmPersonFORM["name"] not in self.LINKEDFORM.keys():
            PersonForm = clsForms.clsRecordForm(self, self.DBConnection, frmPersonFORM, frmPersonCONTROLS)
            self.LINKEDFORM.update({frmPersonFORM["name"]: PersonForm})
            PersonForm.show(True)

    def edit_skill_click(self, event):
        #
        #   Skill Add/Edit/Delete
        #
        if frmSkillFORM["name"] not in self.LINKEDFORM.keys():
            SkillForm = clsForms.clsRecordForm(self, self.DBConnection, frmSkillFORM, frmSkillCONTROLS)
            self.LINKEDFORM.update({frmSkillFORM["name"]: SkillForm})
            SkillForm.show(True)

    def edit_project_click(self, event):
        #
        #   Project Add/Edit/Delete
        #
        if frmProjectFORM["name"] not in self.LINKEDFORM.keys():
            ProjectForm = clsForms.clsRecordForm(self, self.DBConnection, frmProjectFORM, frmProjectCONTROLS)
            self.LINKEDFORM.update({frmProjectFORM["name"]: ProjectForm})
            ProjectForm.show(True)

    def edit_project_task_click(self, event):
        if frmProjectTaskFORM["name"] not in self.LINKEDFORM.keys():
            ProjectTaskForm = clsForms.clsRecordForm(self, self.DBConnection, frmProjectTaskFORM, frmProjectTaskCONTROLS)
            self.LINKEDFORM.update({frmProjectTaskFORM["name"]: ProjectTaskForm})
            ProjectTaskForm.show(True)

    def edit_project_skill_click(self, event):
        if frmProjectSkillFORM["name"] not in self.LINKEDFORM.keys():
            ProjectSkillForm = clsForms.clsRecordForm(self, self.DBConnection, frmProjectSkillFORM, frmProjectSkillCONTROLS)
            self.LINKEDFORM.update({frmProjectSkillFORM["name"]: ProjectSkillForm})
            ProjectSkillForm.show(True)

    def bind_form_controls(self):
        self.FORM.Bind(wx.EVT_BUTTON, self.edit_church_click, self.CONTROLID["btnEditChurch"])

        self.FORM.Bind(wx.EVT_BUTTON, self.edit_person_click, self.CONTROLID["btnEditPerson"])

        self.FORM.Bind(wx.EVT_BUTTON, self.edit_skill_click, self.CONTROLID["btnEditSkill"])

        self.FORM.Bind(wx.EVT_BUTTON, self.edit_project_click, self.CONTROLID["btnEditProject"])
        self.FORM.Bind(
            wx.EVT_BUTTON,
            self.edit_project_task_click,
            self.CONTROLID["btnEditProjectTask"],
        )
        self.FORM.Bind(
            wx.EVT_BUTTON,
            self.edit_project_skill_click,
            self.CONTROLID["btnEditProjectSkill"],
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
frmMainFORM = MainForm(None, ChurchDBConnection, frmProjectMainFORM, frmProjectMainCONTROLS)
frmMainFORM.FORM.Centre()
frmMainFORM.show(True)

app.MainLoop()
