# !/usr/bin/env python3
#   frmChurch.py - Church Forms Classes
# 	Rev. Jonathan C. Watt
# 	July 1, 2021

import wx
import wx.dataview
from wx.core import CONTROL_ISDEFAULT, Control, ID_ANY, SaveFileSelector, StaticText
import mysql
import json

import clsValidators
import clsDB


# <TODO> Documentation for clsForm
#
#   clsForm - Form Class
#       Creates a form and displays controls according to formdescriptin & controldescription disctionaries
#
#   Parameters:
#       parent - Parent ID for this form ('None' for top level form)
#
#       DBConnection - prviously defined DB Connection (Maria or MySQL)
#
#       formdescription - Dictionary Containing data about form
#           'FORM' - data to pass wx.Frame (see wxPython documentation) <TODO> add URL
#           'EXTRA' - other data about the form
#
#       controldesdescriptions - Dictionary contianing Screen fields
#           'CONTROL' - data to pass wx.<field control> (see wxPython documentation)  <TODO> add url
#           'EXTRA' - other data about the control
#
#

#
#   Functions
#
wxpythoncallparmameters = {
    "Frame": ["title", "pos", "size", "style", "name"],
    "StaticText": ["label", "pos", "size", "style", "name"],
    "TextCtrl": ["value", "pos", "size", "style", "validator", "name"],
    "ComboBox": ["value", "pos", "size", "choices", "style", "validator", "name"],
    "CheckBox": ["label", "pos", "size", "style", "validator", "name"],
    "CheckListBox": [
        "value",
        "pos",
        "size",
        "choices",
        "style",
        "validator",
        "name",
    ],
    "Button": ["label", "pos", "size", "style", "validator", "name"],
    "DataViewListCtrl": ["pos", "size", "style", "validator"],
    "btnClose": ["label", "pos", "size", "style", "validator", "name"],
    "btnNextRec": ["label", "pos", "size", "style", "validator", "name"],
    "btnPrevRec": ["label", "pos", "size", "style", "validator", "name"],
    "btnDelete": ["label", "pos", "size", "style", "validator", "name"],
    "btnUpdate": ["label", "pos", "size", "style", "validator", "name"],
    "btnNew": ["label", "pos", "size", "style", "validator", "name"],
}


def getcontrolparameters(controldictionary):
    newdict = {}
    for key in wxpythoncallparmameters[controldictionary["type"]]:
        if key in controldictionary.keys():
            newdict.update({key: controldictionary[key]})
    return newdict


class clsForm:
    #    PARENT - Calling clsForm object
    #    FORM - wxPython Frame for this form
    #    SUBFORM - Dictionary of Subforms called by this form {formname:id}
    #    DBConnection - SQL Database Connection
    #    TABLENAME - Name of the Table for this form
    #    SQL - Default Query for this form

    #    FORMDESCRIPTION - Dictionary containing Form Description - see CMFormDescriptions.py
    #    CONTROLDESCRIPTION - Dictionary containing Form Control Descriptions - see CMFormDescriptions.py
    #    CONTROLID - Dictinary containing the Control ID for every Control on this form {ControlName:ID}

    #    RECORD - Record Class - See clsDB.py

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
        self.FORM = wx.Frame(
            parentform, wx.ID_ANY, **getcontrolparameters(self.FORMDESCRIPTION)
        )

        #
        #   Check for Form without a Record / Table (i.e. Main form with Menu Only)
        #
        try:
            self.TABLENAME = self.FORMDESCRIPTION["tablename"]
            try:
                self.SQL = self.FORMDESCRIPTION["SQL"]
            except:
                self.SQL = "SELECT * FROM " + self.TABLENAME + ";"
        except:
            self.TABLENAME = ""

        if self.TABLENAME != "":
            if sql != "":
                self.SQL = sql
            self.RECORD = clsDB.clsRecord(self.DBConnection, self.TABLENAME, self.SQL)

        self.update_data_to_form(updatecontrolid=True)

        #
        # Bind all the Controls (for sub-classes to inherit)
        #
        self.bind_form_controls()

    def show(self, tf):
        self.FORM.Show(True)

    def get_combobox_by_index(self, controldescription):
        if "cbSQL" in controldescription.keys():
            SQL = controldescription["cbSQL"]
            cursor = self.DBConnection.cursor()
            cursor.execute(SQL)
            rows = cursor.fetchall()
            cblist = {}
            for row in rows:
                cblist.update({row[0]: row[1]})
        else:
            cblist = {}
        return cblist

    def get_combobox_by_choices(self, controldescription):
        if "cbSQL" in controldescription.keys():
            sellist = list(self.get_combobox_by_index(controldescription).values())
        else:
            sellist = []
        return sellist

    def get_comobox_choices_with_index(self, controldescription):
        if "cbSQL" in controldescription.keys():
            SQL = controldescription["cbSQL"]
            cursor = self.DBConnection.cursor()
            cursor.execute(SQL)
            rows = cursor.fetchall()
            cblist = {}
            for row in rows:
                cblist.update({row[1]: row[0]})
        else:
            cblist = {}
        return cblist

    def translate_combobox_to_text(self, controldescription, key):
        value = self.RECORD.get_field_by_name(key)
        if value == "":
            return ""
        elif "cbSQL" in controldescription.keys():
            indexed = self.get_combobox_by_index(controldescription)
            choices = list(indexed.values())
            if value.isnumeric():
                value = int(value)
            return indexed[value]
        elif "choices" in controldescription.keys():
            choices = controldescription["choices"]
            if value in choices:
                return value
            else:
                return ""
        else:
            return ""

    def translate_combobox_to_key(self, controldescription, key):
        value = self.CONTROLID[key].GetValue()
        keys = controldescription.keys()
        if "cbSQL" in controldescription.keys():
            choiceswithindex = self.get_comobox_choices_with_index(controldescription)
            return choiceswithindex[value]
        return value

    def update_form_fields(self, key):
        ctl = None
        localcontroldict = getcontrolparameters(self.CONTROLDESCRIPTION[key])
        if self.CONTROLDESCRIPTION[key]["type"] == "StaticText":
            if key not in self.CONTROLID.keys():
                ctl = wx.StaticText(self.FORM, wx.ID_ANY, **localcontroldict)

        #        elif self.CONTROLDESCRIPTION[key]["type"] == "StaticBitmap":
        #            if key not in self.CONTROLID.keys():
        #                fld = self.RECORD.get_field_by_name("Picture")
        #                bitmap = wxBitmapFromImage( fld )
        #                ctl = wx.StaticBitmap(self.FORM, wx.ID_ANY, **localcontroldict)

        elif self.CONTROLDESCRIPTION[key]["type"] == "TextCtrl":
            if key not in self.CONTROLID.keys():
                localcontroldict.update({"value": self.RECORD.get_field_by_name(key)})
                ctl = wx.TextCtrl(self.FORM, wx.ID_ANY, **localcontroldict)
            else:
                ctl = self.CONTROLID[key]

        elif self.CONTROLDESCRIPTION[key]["type"] == "ComboBox":
            if key not in self.CONTROLID.keys():
                if "choices" not in localcontroldict.keys():
                    choices = self.get_combobox_by_choices(localcontroldict)
                    localcontroldict.update({"choices": choices})
                ctl = wx.ComboBox(self.FORM, wx.ID_ANY, **localcontroldict)
            else:
                ctl = self.CONTROLID[key]
            ctl.SetValue(self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][key])

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

        else:  # <todo>Need better error trapping here
            print("Skipping ", key, "Type", self.CONTROLDESCRIPTION[key]["type"])

        return ctl

    def update_data_to_form(self, updatecontrolid=False):
        if updatecontrolid:
            self.CONTROLID = {}
        for key in self.CONTROLDESCRIPTION.keys():
            ctl = self.update_form_fields(key)
            if updatecontrolid and ctl != None:
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

    def enable_all_buttons(self):
        for c in self.CONTROLID:
            b = self.CONTROLDESCRIPTION[c]["type"][:3]
            if self.CONTROLDESCRIPTION[c]["type"][:3] == "btn":
                self.CONTROLID[c].Enable()

    def disable_all_buttons(self):
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
        # <TODO> This routine has been disabled by always returning true. It needs to check for changed fields.

        modified = False
        for key in self.CONTROLID.keys():
            tp = self.CONTROLDESCRIPTION[key]["type"]
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
        if self.validate_form() == True:
            for key in self.CONTROLID:
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
                    k = self.translate_combobox_to_key(self.CONTROLDESCRIPTION, key)
                    self.RECORD.RECORDS[self.RECORD.CURRENTRECORD][key] = str(k)

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
        # if self.check_for_modified():
        self.RECORD.next_record()
        self.update_data_to_form()
        self.FORM.Refresh()

    def on_prev_record_click(self, event):
        # if self.check_for_modified():
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

        #
        # <TODO> Decide how to deal with new records.

    def on_close_click(self, event):
        self.FORM.Close()

    def OnClose(self, event):
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
                    # self.SUBFORM.pop(key)
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

#
#   <TODO> Documentation for Record Form.


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
