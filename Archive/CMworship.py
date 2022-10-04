# !/usr/bin/env python3
# 	CMworship.py  Church Manager - Worship v0.1
#   Description <TODO>
#
# 	Rev. Jonathan C. Watt
# 	July 1, 2021

import wx
import mysql
import pprint
import json

import clsDB
from clsDB import parse_SQL
import clsForms
import clsFields
from CMFormDescriptions import (
    frmWorshipMainFORM,
    frmWorshipMainCONTROLS,
    frmHymnUsageCONST,
    frmGetFormDescription,
    frmGetControlDescription,

)

#
#   Classes
#

# <TODO> see if you can make these classes more generic.


class HymnSearchForm(clsForms.clsForm):
    def bind_form_controls(self):
        super().bind_form_controls()

        self.FORM.Bind(wx.EVT_BUTTON, self.search_by_title, self.CONTROLID["btnByTitle"])
        self.FORM.Bind(wx.EVT_BUTTON, self.search_by_hymn, self.CONTROLID["btnByHymn"])
        self.FORM.Bind(wx.EVT_BUTTON, self.search_by_bible, self.CONTROLID["btnByBible"])
        self.FORM.Bind(wx.EVT_BUTTON, self.search_by_category, self.CONTROLID["btnByCategory"])
        self.FORM.Bind(wx.EVT_BUTTON, self.search_by_note, self.CONTROLID["btnByNote"])
        self.FORM.Bind(wx.EVT_BUTTON, self.PARENT.add_hymn, self.CONTROLID["btnAdd"])

    def search_by_hymn(self, event):
        sql = (
            "SELECT ID, CONCAT(HymnalPrefix,Hymn) as Hymn,Title,BibleText,Category,Note FROM vwHymnList WHERE Hymn LIKE '%"
            + self.CONTROLID["Search"].GetValue()
            + "%' ORDER BY Hymn ;"
        )
        self.CONTROLID["dvlHymnList"].ResetSQL(sql)
        self.FORM.Refresh()

    def search_by_title(self, event):
        sql = (
            "SELECT ID, CONCAT(HymnalPrefix,Hymn) as Hymn,Title,BibleText,Category,Note FROM vwHymnList WHERE Title LIKE '%"
            + self.CONTROLID["Search"].GetValue()
            + "%' ORDER BY Hymn ;"
        )
        self.CONTROLID["dvlHymnList"].ResetSQL(sql)
        self.FORM.Refresh()

    def search_by_bible(self, event):
        sql = (
            "SELECT ID, CONCAT(HymnalPrefix,Hymn) as Hymn,Title,BibleText,Category,Note FROM vwHymnList WHERE BibleText LIKE '%"
            + self.CONTROLID["Search"].GetValue()
            + "%' ORDER BY Hymn ;"
        )
        self.CONTROLID["dvlHymnList"].ResetSQL(sql)
        self.FORM.Refresh()

    def search_by_category(self, event):
        sql = (
            "SELECT ID, CONCAT(HymnalPrefix,Hymn) as Hymn,Title,BibleText,Category,Note FROM vwHymnList WHERE Category LIKE '%"
            + self.CONTROLID["Search"].GetValue()
            + "%' ORDER BY Hymn ;"
        )
        self.CONTROLID["dvlHymnList"].ResetSQL(sql)
        self.FORM.Refresh()

    def search_by_note(self, event):
        sql = (
            "SELECT ID, CONCAT(HymnalPrefix,Hymn) as Hymn,Title,BibleText,Category,Note FROM vwHymnList WHERE Note LIKE '%"
            + self.CONTROLID["Search"].GetValue()
            + "%' ORDER BY Hymn ;"
        )
        self.CONTROLID["dvlHymnList"].ResetSQL(sql)
        self.FORM.Refresh()

class HymnUsageForm(clsForms.clsForm):
    def bind_form_controls(self):
        super().bind_form_controls()
        self.FORM.Bind(wx.EVT_BUTTON, self.delete_hymn, self.CONTROLID["btnHymnDelete"])
        self.FORM.Bind(wx.EVT_BUTTON, self.update_hymn, self.CONTROLID['btnHymnUpdate'])

    def open_linked_form(self, lnkdfrm):
        linkedformdescr = {**frmGetFormDescription(lnkdfrm), **self.FORMDESCRIPTION["linkedform"][lnkdfrm]}

        # Check of SQL has {field} in the string
        # fill SQL with with this records values
        if "SQL" in linkedformdescr:
            linkedformdescr = {**linkedformdescr, **{"SQL": parse_SQL(linkedformdescr["SQL"], self.RECORDS)}}

        if lnkdfrm == "frmHymnSearch":
            LinkedForm = HymnSearchForm(
                self,
                self.DBConnection,
                linkedformdescr,
                frmGetControlDescription(lnkdfrm),
                self.FORMDESCRIPTION["linkedform"][lnkdfrm]["controls"],
            )
        else:
            LinkedForm = clsForms.clsForm(
                self,
                self.DBConnection,
                linkedformdescr,
                frmGetControlDescription(lnkdfrm),
                self.FORMDESCRIPTION["linkedform"][lnkdfrm]["controls"],
            )
        LinkedForm.FORM.Show(True)
        self.LINKEDFORM.update({lnkdfrm: LinkedForm})
        self.FORM.Bind(wx.EVT_BUTTON, self.add_hymn, self.LINKEDFORM[lnkdfrm].CONTROLID["btnAdd"])

    def add_hymn(self, event):
        # <TODO> make this prettier.
        r = self.LINKEDFORM["frmHymnSearch"].CONTROLID["dvlHymnList"].GetSelectedRow()
        HymnID = self.LINKEDFORM["frmHymnSearch"].CONTROLID["dvlHymnList"].GetValue(r, 0)
        cursor = self.DBConnection.cursor()
        sql = "SELECT ID, 'UsedAs', concat(HymnalPrefix,Hymn) as Hymn, Title, Note FROM vwHymnList WHERE ID = {};".format(HymnID)
        cursor.execute(sql)
        row = cursor.fetchone()
        column = []
        #column.append("UsedAs")
        for c in range(0, len(row)):
            column.append(str(row[c]))
        self.CONTROLID["dvlHymnUsage"].AppendItem(column)
        cursor.close()
        self.LINKEDFORM["frmHymnSearch"].FORM.Close()

    def delete_hymn(self, event):
        r = self.CONTROLID["dvlHymnUsage"].GetSelectedRow()
        self.CONTROLID["dvlHymnUsage"].DeleteItem(r)

    def update_hymn(self,event):
        lnkdfrm = "frmHymnUsage"
        r = self.CONTROLID["dvlHymnUsage"].GetSelectedRow()
        if r == -1:
            return
        ID = self.CONTROLID["dvlHymnUsage"].GetValue(r, 0)

        linkedformdescr = {**frmGetFormDescription(lnkdfrm), **self.FORMDESCRIPTION["linkedform"][lnkdfrm]}

        # Check of SQL has {field} in the string
        # fill SQL with with this records values
        if "SQL" in linkedformdescr:
            linkedformdescr.pop("SQL")

        LinkedForm = clsForms.clsForm(
            self,
            self.DBConnection,
            linkedformdescr,
            frmGetControlDescription(lnkdfrm),
            ["Close"],
        )

        CD = {
            "name": "btnUpdateRec",
            "type": "Button",
            "pos": wx.Point(10, frmHymnUsageCONST["FormButtonRow"]),
            "label": "Update Service",
        }

        LinkedForm.CONTROLDESCRIPTION.update({"btnUpdateRec":CD})
        fld = clsField(LinkedForm, wx.ID_ANY, CD, self.DBConnection)
        LinkedForm.CONTROLID.update({"btnUpdateRec": fld.FIELD})
        LinkedForm.FORM.Bind(wx.EVT_BUTTON, self.update_record, fld.FIELD)

        # Hymn name "ReadOnly"

        LinkedForm.FORM.Show(True)
        self.LINKEDFORM.update({lnkdfrm: LinkedForm})

    def update_record(self,event):
        print ("update_record")

class ServiceForm(clsForms.clsForm):
    def open_linked_form(self, lnkdfrm):
        linkedformdescr = {**frmGetFormDescription(lnkdfrm), **self.FORMDESCRIPTION["linkedform"][lnkdfrm]}

        # Check of SQL has {field} in the string
        # fill SQL with with this records values
        if "SQL" in linkedformdescr:
            linkedformdescr = {**linkedformdescr, **{"SQL": parse_SQL(linkedformdescr["SQL"], self.RECORDS)}}

        if lnkdfrm == "frmHymnUsageDisplay":
            LinkedForm = HymnUsageForm(
                self,
                self.DBConnection,
                linkedformdescr,
                frmGetControlDescription(lnkdfrm),
                self.FORMDESCRIPTION["linkedform"][lnkdfrm]["controls"],
            )
        else:
            LinkedForm = clsForms.clsForm(
                self,
                self.DBConnection,
                linkedformdescr,
                frmGetControlDescription(lnkdfrm),
                self.FORMDESCRIPTION["linkedform"][lnkdfrm]["controls"],
            )
        LinkedForm.FORM.Show(True)
        self.LINKEDFORM.update({lnkdfrm: LinkedForm})

    def bind_form_controls(self):
        super().bind_form_controls()
        self.FORM.Bind(wx.EVT_COMBOBOX, self.on_checklist_change, self.CONTROLID["CheckListID"])
        self.FORM.Bind(wx.EVT_COMBOBOX, self.on_propers_change, self.CONTROLID["PropersID"])

    def on_checklist_change(self, event):
        cursor = self.DBConnection.cursor()
        sql = "SELECT CheckListValue FROM tblCheckList WHERE ID = {}".format(self.CONTROLID["CheckListID"].GetValue())
        cursor.execute(sql)
        row = cursor.fetchone()
        if row != None:
            checklist = json.loads(row[0])
            self.CONTROLID["CheckList"].SetValue(row[0])

    def on_propers_change(self, event):
        value = self.CONTROLID["PropersID"].GetValue()
        self.RECORDS.RECORD.setfieldvalue("PropersID",value)
        self.fill_subforms()

class MainForm(clsForms.clsForm):
    def open_linked_form(self, lnkdfrm):
        linkedformdescr = {**frmGetFormDescription(lnkdfrm), **self.FORMDESCRIPTION["linkedform"][lnkdfrm]}

        # Check of SQL has {field} in the string
        # fill SQL with with this records values
        if "SQL" in linkedformdescr:
            linkedformdescr = {**linkedformdescr, **{"SQL": parse_SQL(linkedformdescr["SQL"], self.RECORDS)}}

        if lnkdfrm == "frmService":
            LinkedForm = ServiceForm(
                self,
                self.DBConnection,
                linkedformdescr,
                frmGetControlDescription(lnkdfrm),
                self.FORMDESCRIPTION["linkedform"][lnkdfrm]["controls"],
            )
        else:
            LinkedForm = clsForms.clsForm(
                self,
                self.DBConnection,
                linkedformdescr,
                frmGetControlDescription(lnkdfrm),
                self.FORMDESCRIPTION["linkedform"][lnkdfrm]["controls"],
            )
        LinkedForm.FORM.Show(True)
        self.LINKEDFORM.update({lnkdfrm: LinkedForm})


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
# frmMainFORM = MainForm(None, ChurchDBConnection, frmWorshipMainFORM, frmWorshipMainCONTROLS)
MainFORM = MainForm(None, ChurchDBConnection, frmWorshipMainFORM, frmWorshipMainCONTROLS, controls=["Close"])
MainFORM.FORM.Center()
MainFORM.FORM.Show(True)

app.MainLoop()
