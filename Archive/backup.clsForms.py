# !/usr/bin/env python3
#
#   frmForms.py - Church Manager Forms Classes
#
# 	Rev. Jonathan C. Watt
# 	July 1, 2021
#

import wx
import wx.dataview
from wx.core import CONTROL_ISDEFAULT, Control, ID_ANY, SaveFileSelector, StaticText
import mysql
import json
from datetime import date

import clsValidators
import clsDB

#
#   Global Variables and Functions
#
#
#   This dictionary defines the fields passed to the wxPython controls.
#
wxpythoncallparmameters = {
    "Frame": ["title", "pos", "size", "style", "name"],
    "StaticText": ["label", "pos", "size", "style", "name"],
    "TextCtrl": ["value", "pos", "size", "style", "validator", "name"],
    "ComboBox": ["value", "pos", "size", "choices", "style", "validator", "name"],
    "CheckBox": ["label", "pos", "size", "style", "validator", "name"],
    "CheckListBox": ["value","pos","size","choices","style","validator","name",],
    "Button": ["label", "pos", "size", "style", "validator", "name"],
    "DataViewListCtrl": ["pos", "size", "style", "validator"],
    "btnClose": ["label", "pos", "size", "style", "validator", "name"],
    "btnNextRec": ["label", "pos", "size", "style", "validator", "name"],
    "btnPrevRec": ["label", "pos", "size", "style", "validator", "name"],
    "btnDelete": ["label", "pos", "size", "style", "validator", "name"],
    "btnUpdate": ["label", "pos", "size", "style", "validator", "name"],
    "btnNew": ["label", "pos", "size", "style", "validator", "name"],
}


#
#   This function strips away the parameters that are not passed to the wx.<controls>
#   so that the control can be called without errors and CMFormDescriptions.py
#   can contain all the dynamic information about the field.
#       (See table above *wxpythoncallparmameters)
#
def getcontrolparameters(controldictionary):
    newdict = {}
    for key in wxpythoncallparmameters[controldictionary["type"]]:
        if key in controldictionary.keys():
            newdict.update({key: controldictionary[key]})
    return newdict


#
# clsForm: Process a form
#
#   Class Variables.
#       PARENT - Calling clsForm object
#       FORM - wxPython Frame for this form
#       SUBFORM - Dictionary of Subforms called by this form {formname:id}
#       DBConnection - SQL Database Connection
#       TABLENAME - Name of the Table for this form
#       SQL - Default Query for this form
#       CONTROLID - Dictinary containing the Control ID for every Control on this form {ControlName:ID}
#
#   Parameters
#       self
#       parent - calling form or "none"
#       dbconnection - DB Connection (MySQL)
#       formdescription - Dictionary containing Form Description - see CMFormDescriptions.py
#       controldescription - Dictionary containing Form Control Descriptions - see CMFormDescriptions.py
#       sql - SQL Query overirde from the caller
#
#   Uses
#       RECORD - Record Class - See clsDB.py
#
class clsForm:
    def __init__(
        self, parent, dbconnection, formdescription, controldescription, sql=""
    ):

        self.DBConnection = dbconnection  # Save the Connection Locally
        self.FORMDESCRIPTION = formdescription
        self.CONTROLDESCRIPTION = controldescription
        self.PARENT = parent
        self.SUBFORM = {}

        if self.PARENT == None:
            parentform = None
        else:
            parentform = self.PARENT.FORM
        localcontrol = getcontrolparameters(self.FORMDESCRIPTION)
        self.FORM = wx.Frame(
            parentform, wx.ID_ANY, **localcontrol)

        #
        #   Check for Form without a Record / Table (i.e. Main form with Menu Only)
        #
        self.TABLENAME = ""
        if "tablename" in self.FORMDESCRIPTION:
            self.TABLENAME = self.FORMDESCRIPTION["tablename"]
            if "SQL" in self.FORMDESCRIPTION:
                self.SQL = self.FORMDESCRIPTION["SQL"]
            else:
                self.SQL = "SELECT * FROM " + self.TABLENAME + ";"

        if self.TABLENAME != "":
            if sql != "":
                self.SQL = sql
            self.RECORD = clsDB.clsRecord(self.DBConnection, self.TABLENAME, self.SQL)
            if len(self.RECORD.RECORDS) == 0:
                self.RECORD.CURRENTRECORD = 0
                self.RECORD.RECORDS = {0:{}}
                for key in self.CONTROLDESCRIPTION:
                    if (key[0:3] != "lbl") and (key[0:3] != "btn"):
                        self.RECORD.RECORDS[0].update({key:""})

        self.CONTROLID = {}
        self.update_data_to_form()

        #
        # Bind all the Controls (for sub-classes to inherit)
        #
        self.bind_form_controls()

            

    def show(self, tf):
        self.FORM.Show(True)

    #
    #   build a choices list for the field specified by "cbSQL" in CMFormDescriptions.py
    #   if "choices" isn't defined.
    #
    def get_combobox_choices(self, key):
        choicesdict = {}
        cursor = self.DBConnection.cursor()
        cbSQL = self.CONTROLDESCRIPTION[key]["cbSQL"]
        cursor.execute(cbSQL)
        rows = cursor.fetchall()
        for row in rows:
            choicesdict.update({row[0]: row[1]})
        return choicesdict

    #
    #   Lookup data for a field based on "lkpSQL" specified in CMFormsDescripions.py
    #
    def lookup_field(self, key):
        cursor = self.DBConnection.cursor()
        sql = self.CONTROLDESCRIPTION[key]['lkpSQL']
        whereloc = sql.find("<<where>>")
        if whereloc != -1:
            where = self.RECORD.get_field_by_name(key)
            sql = sql.replace("<<where>>",where)
        cursor.execute(sql)
        row = cursor.fetchone()
        coltype = cursor.description[0][0]
        # Format the DateTime and Date type fields to string. All data passed to wxPython
        # field routines must be string.
        if coltype == "DateTime":
            value = row[0].strftime("%Y-%m-%d %H:%M %p")
        elif coltype == "Date":
            value = row[0].strftime("%Y-%m-%m")
        else:
            value = row[0]
        return value

    def update_form_fields(self, key):
        ctl = None
        localcontroldict = getcontrolparameters(self.CONTROLDESCRIPTION[key])
        if self.CONTROLDESCRIPTION[key]["type"] == "StaticText":
            if key not in self.CONTROLID.keys():
                if "date" in self.CONTROLDESCRIPTION[key]:
                    label = date.today().strftime("%Y-%m-%m")
                    localcontroldict.update({"label": label})
                elif "lkpSQL" in self.CONTROLDESCRIPTION[key].keys():
                    label = self.lookup_field(key)
                    localcontroldict.update({"label": label})
                ctl = wx.StaticText(self.FORM, wx.ID_ANY, **localcontroldict)
        #        elif self.CONTROLDESCRIPTION[key]["type"] == "StaticBitmap":   # <TODO> Add for pictures of members and families. 
        #            if key not in self.CONTROLID.keys():
        #                fld = self.RECORD.get_field_by_name("Picture")
        #                bitmap = wxBitmapFromImage( fld )
        #                ctl = wx.StaticBitmap(self.FORM, wx.ID_ANY, **localcontroldict)

        elif self.CONTROLDESCRIPTION[key]["type"] == "TextCtrl":
            if key not in self.CONTROLID.keys():
                if "lkpSQL" in self.CONTROLDESCRIPTION[key].keys():
                    value = self.lookup_field(key)
                else:
                    value = self.RECORD.get_field_by_name(key)
                localcontroldict.update({"value": value})
                ctl = wx.TextCtrl(self.FORM, wx.ID_ANY, **localcontroldict)
            else:
                ctl = self.CONTROLID[key]
                if "lookup" in self.CONTROLDESCRIPTION[key].keys():
                    value = self.lookup_field(key)
                else:
                    value = self.RECORD.get_field_by_name(key)
                ctl.SetValue(value)

        elif self.CONTROLDESCRIPTION[key]["type"] == "ComboBox":
            if key not in self.CONTROLID.keys():
                if "choices" in localcontroldict.keys():
                    localcontroldict.update(
                        {"value": self.RECORD.get_field_by_name(key)}
                    )
                elif "cbSQL" in self.CONTROLDESCRIPTION[key].keys():
                    choicesdict = self.get_combobox_choices(key)
                    localcontroldict.update({"choices": list(choicesdict.values())})
                    localcontroldict.update(
                        {"value": choicesdict[int(self.RECORD.get_field_by_name(key))]} # <TODO> for choices where choces dict isn't valid for all values. 
                                                                                        # i.e. a PropersID from outside of the current liturgical year -A,B,C
                    )
                ctl = wx.ComboBox(self.FORM, wx.ID_ANY, **localcontroldict)
            else:
                ctl = self.CONTROLID[key]
                if "cbSQL" in self.CONTROLDESCRIPTION[key].keys():
                    choicesdict = self.get_combobox_choices(key)
                    value = choicesdict[int(self.RECORD.get_field_by_name(key))]
                else:
                    value = self.RECORD.get_field_by_name(key)
                ctl.SetValue(value)

        elif self.CONTROLDESCRIPTION[key]["type"] == "CheckBox":
            if key not in self.CONTROLID.keys():
                ctl = wx.CheckBox(self.FORM, wx.ID_ANY, **localcontroldict)
            else:
                ctl = self.CONTROLID[key]

            if self.RECORD.get_field_by_name(key) == True:
                ctl.SetValue(wx.CHK_CHECKED)
            else:
                ctl.SetValue(wx.CHK_UNCHECKED)

        elif self.CONTROLDESCRIPTION[key]["type"] == "CheckListBox":
            if key not in self.CONTROLID.keys():
                fld = self.RECORD.get_field_by_name(key)
                if fld != "":
                    checklist = json.loads(fld)
                    clkeys = list(checklist.keys())
                else:
                    clkeys = []
                localcontroldict.update({"choices": clkeys})
                ctl = wx.CheckListBox(self.FORM, wx.ID_ANY, **localcontroldict)
                if fld != "":
                    for c in checklist.keys():
                        if checklist[c] == "True":
                            ctl.Check(ctl.FindString(c), True)

            else:
                ctl = self.CONTROLID[key]
                fld = self.RECORD.get_field_by_name(key)
                if fld != "":
                    checklist = json.loads(fld)
                    clkeys = list(checklist.keys())
                else:
                    clkeys = []
                ctl.Destroy()  # Since the Checklist is potentially different for each record
                # we must recreate a new control.
                localcontroldict.update({"choices": clkeys})

                ctl = wx.CheckListBox(self.FORM, wx.ID_ANY, **localcontroldict)
                self.CONTROLID[key] = ctl
                if fld != "":
                    for c in checklist.keys():
                        if checklist[c] == "True":
                            ctl.Check(ctl.FindString(c), True)

        elif self.CONTROLDESCRIPTION[key]["type"] == "Button":
            if key not in self.CONTROLID.keys():
                ctl = wx.Button(self.FORM, wx.ID_ANY, **localcontroldict)
            else:
                ctl = self.CONTROLID[key]

        elif self.CONTROLDESCRIPTION[key]["type"] == "DataViewListCtrl":
            if key not in self.CONTROLID.keys():
                ctl = wx.dataview.DataViewListCtrl(
                    self.FORM, wx.ID_ANY, **localcontroldict
                )
            else:
                ctl = self.CONTROLID[key]

            i = 0
            for column in localcontroldict["columns"]:
                ctl.AppendTextColumn(
                    column,
                    width=localcontroldict["columnwidth"][i],
                )
                i += 1

            select = self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][
                localcontroldict["select"]
            ]

            for row in self.RECORD.RECORDS.keys():
                if select == self.RECORD.RECORDS[row][localcontroldict["select"]]:
                    data = []
                    for column in localcontroldict["columns"]:
                        data.append(self.RECORD.RECORDS[row][column])
                    ctl.AppendItem(data)

        #
        #   Pre-Defined Buttons
        #
        elif self.CONTROLDESCRIPTION[key]["type"] == "btnClose":
            if key not in self.CONTROLID.keys():
                ctl = wx.Button(self.FORM, wx.ID_ANY, **localcontroldict)

                ctl.SetLabel("Close")
                self.FORM.Bind(wx.EVT_BUTTON, self.on_close_click, ctl)
            else:
                ctl = self.CONTROLID[key]

        elif self.CONTROLDESCRIPTION[key]["type"] == "btnNextRec":
            if key not in self.CONTROLID.keys():
                ctl = wx.Button(self.FORM, wx.ID_ANY, **localcontroldict)

                ctl.SetLabel("&Next")
                self.FORM.Bind(wx.EVT_BUTTON, self.on_next_record_click, ctl)
            else:
                ctl = self.CONTROLID[key]

        elif self.CONTROLDESCRIPTION[key]["type"] == "btnPrevRec":
            if key not in self.CONTROLID.keys():
                ctl = wx.Button(self.FORM, wx.ID_ANY, **localcontroldict)

                ctl.SetLabel("&Prev")
                self.FORM.Bind(wx.EVT_BUTTON, self.on_prev_record_click, ctl)
            else:
                ctl = self.CONTROLID[key]

        elif self.CONTROLDESCRIPTION[key]["type"] == "btnUpdate":
            if key not in self.CONTROLID.keys():
                ctl = wx.Button(self.FORM, wx.ID_ANY, **localcontroldict)

                ctl.SetLabel("&Update")
                self.FORM.Bind(wx.EVT_BUTTON, self.on_update_record_click, ctl)
            else:
                ctl = self.CONTROLID[key]

        elif self.CONTROLDESCRIPTION[key]["type"] == "btnDelete":
            if key not in self.CONTROLID.keys():
                ctl = wx.Button(self.FORM, wx.ID_ANY, **localcontroldict)

                ctl.SetLabel("&Delete")
                self.FORM.Bind(wx.EVT_BUTTON, self.on_delete_record_click, ctl)
            else:
                ctl = self.CONTROLID[key]

        elif self.CONTROLDESCRIPTION[key]["type"] == "btnNew":
            if key not in self.CONTROLID.keys():
                ctl = wx.Button(self.FORM, wx.ID_ANY, **localcontroldict)

                ctl.SetLabel("&New")
                self.FORM.Bind(wx.EVT_BUTTON, self.on_new_record_click, ctl)
            else:
                ctl = self.CONTROLID[key]

        else:  # <TODO> Need better error trapping here
            print("Skipping ", key, "Type", self.CONTROLDESCRIPTION[key]["type"])

        if "fcolor" in self.CONTROLDESCRIPTION[key]:
            ctl.SetForegroundColour(self.CONTROLDESCRIPTION[key]['fcolor'])
        if "bcolor" in self.CONTROLDESCRIPTION[key]:
            ctl.SetBackgroundColour(self.CONTROLDESCRIPTION[key]['bcolor'])

        # Check for Read Only Fields
        if "readonly" in self.CONTROLDESCRIPTION[key].keys():
            ctl.Disable()

        return ctl

    def update_data_to_form(self):
        for key in self.CONTROLDESCRIPTION.keys():
            ctl = self.update_form_fields(key)
            if ctl != None:
                if ctl not in self.CONTROLID.keys():
                    self.CONTROLID.update({key: ctl})

    def bind_form_controls(self):
        # for binding sub-class controls

        #
        # Set up the Close Event always (click on [x])
        #
        self.FORM.Bind(wx.EVT_CLOSE, self.OnClose)

    def disable_button(self, name):
        self.CONTROLID[name].Disable()

    def enable_all_buttons(self):  # pre-defined buttons
        for c in self.CONTROLID:
            b = self.CONTROLDESCRIPTION[c]["type"][:3]
            if self.CONTROLDESCRIPTION[c]["type"][:3] == "btn":
                self.CONTROLID[c].Enable()

    def disable_all_buttons(self):  # pre-defined buttons
        for c in self.CONTROLID:
            b = self.CONTROLDESCRIPTION[c]["type"][:3]
            if self.CONTROLDESCRIPTION[c]["type"][:3] == "btn":
                self.CONTROLID[c].Disable()

    def validate_form(self):
        formvalidate = self.FORM.Validate()
        controlsvalidate = self.FORM.TransferDataFromWindow()
        if formvalidate and controlsvalidate:
            return True
        else:
            return False

    def check_for_modified(self):
        # <TODO> This routine is not called. Needs to be introduced to check if fields are modified
        #   when moving to the next record or exiting the form.
        modified = False
        for key in self.CONTROLID.keys():
            tp = self.CONTROLDESCRIPTION[key]["type"]
            # <TODO> use if x not in self.CONTROLDESCRIPTION[key]["type"] for better logic.
            if (tp != "Button") and (tp[:3] != "btn"):
                if self.CONTROLID[key].IsModified():
                    modified = True
        if modified:
            dlg = wx.MessageDialog(
                self.FORM,
                "This record has unsaved data. Do you really want to leave this form?",
                "Leave form",
                wx.OK | wx.CANCEL | wx.ICON_QUESTION,
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                return True
        return False  # always return true

    def on_update_record_click(self, event):
        if (
            self.validate_form() == True
        ):  # this calls validators from clsValidators.py via wxPython.
            for key in self.CONTROLID:
                if "readonly" in self.CONTROLDESCRIPTION[key]:
                    continue

                if self.CONTROLDESCRIPTION[key]["type"] == "TextCtrl":
                    if self.CONTROLID[key].IsMultiLine():
                        lines = ""
                        for line in range(0, self.CONTROLID[key].GetNumberOfLines()):
                            lines = (
                                lines + self.CONTROLID[key].GetLineText(line) + "\r\n"
                            )
                        self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][key] = lines
                    else:
                        self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][
                            key
                        ] = self.CONTROLID[key].GetValue()

                elif self.CONTROLDESCRIPTION[key]["type"] == "ComboBox":
                    if "cbSQL" in self.CONTROLDESCRIPTION[key].keys():
                        value = ""
                        cursor = self.DBConnection.cursor()
                        cursor.execute(self.CONTROLDESCRIPTION[key]["cbSQL"])
                        rows = cursor.fetchall()
                        for row in rows:
                            if row[1] == self.CONTROLID[key].GetValue():
                                value = row[0]
                                break
                    else:
                        value = self.CONTROLID[key].GetValue()
                    self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][key] = str(value)

                elif self.CONTROLDESCRIPTION[key]["type"] == "CheckBox":
                    if self.CONTROLID[key].GetValue() == wx.CHK_CHECKED:
                        self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][key] = "1"
                    else:
                        self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][key] = "0"

                elif self.CONTROLDESCRIPTION[key]["type"] == "CheckListBox":
                    checklist = self.CONTROLID[key].GetStrings()
                    checked = self.CONTROLID[key].GetCheckedStrings()
                    di = {}
                    for c in checklist:
                        if c in checked:
                            di.update({c: "True"})
                        else:
                            di.update({c: "False"})
                    j = json.dumps(di)
                    self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][key] = json.dumps(di)

            self.RECORD.update_current_record()
            self.enable_all_buttons()
        else:
            self.disable_all_buttons()
            self.CONTROLID["btnUpdate"].Enable()
            self.CONTROLID["btnClose"].Enable()
            self.FORM.Refresh()

    def on_next_record_click(self, event):
        # <TODO> if self.check_for_modified():
        self.RECORD.next_record()
        self.update_data_to_form()
        self.FORM.Refresh()

    def on_prev_record_click(self, event):
        # <TODO> if self.check_for_modified():
        self.RECORD.prev_record()
        self.update_data_to_form()
        self.FORM.Refresh()

    def on_delete_record_click(self, event):
        dlg = wx.MessageDialog(
            self.FORM,
            "Do you really want to DELETE this record?",
            "Confirm Exit",
            wx.OK | wx.CANCEL | wx.ICON_QUESTION,
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.RECORD.delete_record()
            self.update_data_to_form()
            self.FORM.Refresh()

    def on_new_record_click(self, event):
        self.RECORD.new_blank_record()
        self.update_data_to_form()
        self.disable_all_buttons()
        self.CONTROLID["btnUpdate"].Enable()
        self.CONTROLID["btnClose"].Enable()
        self.FORM.Refresh()

    def on_close_click(self, event):
        self.FORM.Close()

    def OnClose(self, event):  # Closes all children.
        if event.CanVeto():
            dlg = wx.MessageDialog(
                self.FORM,
                "Do you really want to close this form?",
                "Confirm Exit",
                wx.OK | wx.CANCEL | wx.ICON_QUESTION,
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                for key in self.SUBFORM.copy().keys():
                    self.SUBFORM[key].OnClose(event)
                    if event.GetVeto():
                        event.Veto()
                        return
                self.FORM.Destroy()
                if self.PARENT != None:
                    self.PARENT.SUBFORM.pop(self.FORM.Name)
                return
            else:
                event.Veto()
                return
        self.FORM.Destroy()
        if self.PARENT != None:
            self.PARENT.SUBFORM.pop(self.FORM.Name)


#
# clsRecordForm: Process a form including predefined buttons for navigating through a records in a collection.
#
#   Class Variables.
#       PARENT - Calling clsForm object
#       FORM - wxPython Frame for this form
#       SUBFORM - Dictionary of Subforms called by this form {formname:id}
#       DBConnection - SQL Database Connection
#       TABLENAME - Name of the Table for this form
#       SQL - Default Query for this form
#       CONTROLID - Dictinary containing the Control ID for every Control on this form {ControlName:ID}
#
#   Parameters
#       self
#       parent - calling form or "none"
#       dbconnection - DB Connection (MySQL)
#       formdescription - Dictionary containing Form Description - see CMFormDescriptions.py
#       controldescription - Dictionary containing Form Control Descriptions - see CMFormDescriptions.py
#       sql - SQL Query overirde from the caller
#
#   Uses
#       RECORD - Record Class - See clsDB.py
#
class clsRecordForm(clsForm):
    def __init__(
        self, parent, dbconnection, formdescription, controldescription, sql=""
    ):
        btnStandardCONTROL = {
            "btnClose": {
                "type": "btnClose",
                "label": "Close",
                "pos": wx.Point(0, 0),
                "name": "btnClose",
            },
            "btnNextRec": {
                "type": "btnNextRec",
                "label": "Next",
                "pos": wx.Point(0, 0),
                "name": "btnNextRec",
            },
            "btnPrevRec": {
                "type": "btnPrevRec",
                "label": "Prev",
                "pos": wx.Point(0, 0),
                "name": "btnPrevRec",
            },
            "btnUpdate": {
                "type": "btnUpdate",
                "label": "Update",
                "pos": wx.Point(0, 0),
                "name": "btnUpdate",
            },
            "btnDelete": {
                "type": "btnDelete",
                "label": "Delete",
                "pos": wx.Point(0, 0),
                "name": "btnDelete",
            },
            "btnNew": {
                "type": "btnNew",
                "Label": "New",
                "pos": wx.Point(0, 0),
                "name": "btnNew",
            },
        }
        cd = {}

        pos = formdescription["size"]

        # <TODO> change to be more generic for positioning.
        x = pos[0]
        y = pos[1] - 75
        for key in btnStandardCONTROL.keys():
            x -= 100
            btnStandardCONTROL[key].update({"pos": wx.Point(x, y)})

        for key in btnStandardCONTROL.keys():
            controldescription.update({key: btnStandardCONTROL[key]})

        clsForm.__init__(
            self, parent, dbconnection, formdescription, controldescription, sql
        )

    def disable_prev_next(self):
        self.CONTROLID["btnPrevRec"].Disable()
        self.CONTROLID["btnNextRec"].Disable()
