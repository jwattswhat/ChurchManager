"""
    frmFields.py - Church Manager Form Classes

    Rev. Jonathan C. Watt
    September 11, 2021

"""
from mysql.connector import FieldType
import datetime
import json
import os
import pathlib
import itertools
import sys

# import wxpython

import wx
import wx.adv
import wx.dataview

# import framwork

import clsError
from clsConstants import CONST
from clsFont import FONT
from clsConfig import CONFIG
from clsSQL import clsSQL
from clsValidators import setvalidatorfield
import clsDB
from fnUtil import stripcrlf
import clsChoices


def getcontrolparameters(controldictionary):
    """
    This function strips away the parameters that are not passed to the wx.<controls>
    so that the control can be called without errors and CMFormDescriptions.py
    can contain all the dynamic information about the field.
        (See table clsConstants.wxpythoncallparmameters)
    """
    global FONT

    newdict = {}
    if "stylelist" in controldictionary:
        newdict.update({"style": setstylefield(controldictionary["stylelist"])})
    if "validatorstr" in controldictionary:
        newdict.update(
            {"validator": setvalidatorfield(controldictionary["validatorstr"])}
        )

    for key in CONST.wxpythoncallparmameters[controldictionary["type"]]:
        if key in controldictionary.keys():
            newdict.update({key: controldictionary[key]})
    return newdict


def setstylefield(sty):
    """
    This function replaces string "styles" with wxPython constants.
    """
    st = 0
    if "CAPTION" in sty:
        st = st | wx.CAPTION
    if "MINIMIZEBOX" in sty:
        st = st | wx.MINIMIZE_BOX
    if "MAXIMIZEBOX" in sty:
        st = st | wx.MAXIMIZE_BOX
    if "CLOSEBOX" in sty:
        st = st | wx.CLOSE_BOX
    if "MULTILINE" in sty:
        st = st | wx.TE_MULTILINE
    if "DONTWRAP" in sty:
        st = st | wx.TE_DONTWRAP
    if "WORDWRAP" in sty:
        st = st | wx.TE_WORDWRAP
    if "READONLY" in sty:
        st = st | wx.TE_READONLY
    if "PROCESSENTER" in sty:
        st = st | wx.TE_PROCESS_ENTER
    if "PROCESSTAB" in sty:
        st = st | wx.TE_PROCESS_TAB
    if "FLPCHANGEDIR" in sty:
        st = st | wx.FLP_CHANGE_DIR
    if "FLPSMALL" in sty:
        st = st | wx.FLP_SMALL
    if "FLPUSETEXTCTRL" in sty:
        st = st | wx.FLP_USE_TEXTCTRL

    return st


FORMColors = {
    "Warning": {"fcolor": "White", "bcolor": "Red"},
    "Error": {"fcolor": "White", "bcolor": "Red"},
    "Notice": {"fcolor": "Blue", "bcolor": "White"},
    "Normal": {"fcolor": "Black", "bcolor": "White"},
}


class clsField:
    """
    this class processes all the form fields.
        initialization:
            parent - parent calling parent
            id - wxpython ID
            controldescription - dictionary control description (see - )
            dbconnection - database connection
        subclasses:


    """

    PARENT = None
    FIELD = 0
    ID = None
    DBConnection = 0

    def __init__(
        self,
        parent,
        id,
        controldescription,
        dbconnection,
    ):

        self.PARENT = parent
        self.ID = id
        self.DBConnection = dbconnection

        # all fields pre process

        # here the field is parsed according to field "type".
        match controldescription["type"]:
            case "StaticBox":
                self.FIELD = self.clsStaticBox(self, controldescription)
            case "StaticText":
                self.FIELD = self.clsStaticText(self, controldescription)
            case "MultiLine":
                self.FIELD = self.clsMultiLine(self, controldescription)
            case "TextCtrl":
                self.FIELD = self.clsTextCtrl(self, controldescription)
            case "TextNumber":
                self.FIELD = self.clsTextNumber(self, controldescription)
            case "JSON":
                self.FIELD = self.clsJSON(self, controldescription)
            case "ComboBox":
                self.FIELD = self.clsComboBox(self, controldescription)
            case "ListCtrl":
                self.FIELD = self.clsListCtrl(self, controldescription)
            case "ListCtrlID":
                self.FIELD = self.clsListCtrlID(self, controldescription)
            case "CheckBox":
                self.FIELD = self.clsCheckBox(self, controldescription)
            case "CheckListBox":
                self.FIELD = self.clsCheckListBox(self, controldescription)
            case "Button":
                self.FIELD = self.clsButton(self, controldescription)
            case "DataViewListCtrl":
                self.FIELD = self.clsDataListViewCtrl(self, controldescription)
            case "DateTime":
                self.FIELD = self.clsDateTime(self, controldescription)
            case "DatePickerCtrl":
                self.FIELD = self.clsDatePickerCtrl(self, controldescription)
            case "TimePickerCtrl":
                self.FIELD = self.clsTimePickerCtrl(self, controldescription)
            case "FilePickerCtrl":
                self.FIELD = self.clsFilePickerCtrl(self, controldescription)

        #  all fields post process

        # Check for Read Only Fields
        if "readonly" in controldescription:
            self.FIELD.Disable()

    def GetID(self):
        return self.ID

    def GetName(self):
        return self.FIELD.GetName()

    class clsFieldExtra:
        def init_field(self, parent, controldescription):
            self.parent = parent
            self.DIRTY = False
            self.DBConnection = parent.DBConnection
            self.CONTROLDESCRIPTION = controldescription.copy()
            self.choices = clsChoices.clsChoices(
                self.DBConnection, self.CONTROLDESCRIPTION
            )

        def SetValue(self, value):
            if value == None:
                super().SetValue("")
            else:
                super().SetValue(value)

        def ChangeValue(self, value):
            if value == None:
                super().ChangeValue("")
            else:
                super().ChangeValue(value)

        def GetValue(self):
            value = super().GetValue()
            if value == "":
                value = None
            return value

        def SetWarningColor(self):
            self.SetBackgroundColour(FORMColors["Warning"]["bcolor"])
            self.SetForegroundColour(FORMColors["Warning"]["fcolor"])
            self.Refresh()

        def SetNormalColor(self):
            self.SetBackgroundColour(FORMColors["Normal"]["bcolor"])
            self.SetForegroundColour(FORMColors["Normal"]["fcolor"])
            self.Refresh()

    class clsStaticBox(wx.StaticBox, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)
            # statictext preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )
            # self.SetNormalColor()

    class clsStaticText(wx.StaticText, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # statictext preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )

            # statictext postprocess

        def SetValue(self, value):
            if value != None:
                super().SetLabel(value)
            self.SetNormalColor()

    class clsMultiLine(wx.TextCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # textctrl preprocess

            if "stylelist" in controldescription:
                a = ["MULTILINE", "PROCESSENTER", "DONTWRAP"]
                b = list(controldescription["stylelist"])
                c = list(itertools.chain(a, b))  # only keep one of each.
                controldescription["stylelist"] = list(set(c))
            else:
                controldescription.update(
                    {"stylelist": ["MULTILINE", "PROCESSENTER", "DONTWRAP"]}
                )

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )
            self.SetNormalColor()

            # textctrl postprocess

        def SetValue(self, value):
            if value == None:
                super().SetValue("")
            else:
                if type(value) == list:
                    value = "\r\n".join(value)
                super().SetValue(value)

        def ChangeValue(self, value):
            if value == None:
                super().ChangeValue("")
            else:
                super().ChangeValue("\r\n".join(value))

        def GetValue(self):
            value = super().GetValue()
            if value == "":
                value = None
            else:
                value = value.splitlines()
            return value

    class clsTextNumber(wx.TextCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)
            self.controldescription = controldescription
            # textctrl preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(controldescription)
            )
            self.SetNormalColor()

            # textctrl postprocess

        def SetValue(self, value):
            if value == None:
                super().SetValue("")
            else:
                return super().SetValue(self.controldescription["format"].format(value))

        def ChangeValue(self, value):
            if value == None:
                super().ChangeValue("")
            else:
                return super().ChangeValue(
                    self.controldescription["format"].format(value)
                )

        def GetValue(self):
            value = self.choices.getchoicedisplay(super().GetValue())
            if value == "":
                value = None
            return value

    class clsTextCtrl(wx.TextCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # textctrl preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )
            self.SetNormalColor()

            # textctrl postprocess

        def SetValue(self, value):
            if value == None:
                super().SetValue("")
            else:
                super().SetValue(self.choices_choicesID2display(value))

        def ChangeValue(self, value):
            if value == None:
                super().ChangeValue("")
            else:
                super().ChangeValue(str(self.choices.getchoicedisplay(value)))

        def GetValue(self):
            value = self.choices.getchoiceid(super().GetValue())
            if value == "":
                value = None
            return value

    class clsJSON(wx.TextCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # JSON preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )
            self.SetNormalColor()

            # JSON postprocess

    class clsComboBox(wx.ComboBox, clsFieldExtra):
        def __init__(self, parent, controldesc):

            super().init_field(parent, controldesc)

            controldescription = self.CONTROLDESCRIPTION.copy()

            # combobox preproces
            choices = self.choices.Load_Choices(controldescription)
            if choices != None:
                controldescription.update({"choices": choices})

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(controldescription)
            )
            self.SetNormalColor()

            # combobox postprocess

        def Set(self, choices):
            # override to remove EVT_TEXT when the control changes.
            self.parent.PARENT.FORM.Unbind(wx.EVT_TEXT, id=self.GetId())
            super().Set(choices)
            self.parent.PARENT.FORM.Bind(
                wx.EVT_TEXT, self.parent.PARENT._captureevent, self
            )

        def SetValue(self, value):
            if value == None:
                super().SetValue("")
            else:
                if self.choiceslist == None:
                    super().SetValue(value)
                else:
                    disp = self.choiceslist.getdisplaybyid(value)
                    if disp == None:
                        return None
                    super().SetValue(disp)

        def ChangeValue(self, value):
            if value == None:
                super().ChangeValue("")
            else:
                if self.choices.len() == 0:
                    super().ChangeValue(str(value))
                else:
                    disp = self.choices.getchoicedisplay(value)
                    if disp == None:
                        return None
                    super().ChangeValue(disp)

        def GetValueText(self):
            value = super().GetValue()
            if value == "":
                return None
            return value

        def GetValue(self):
            if self.choices.len() == 0:
                value = super().GetValue()
            else:
                value = self.choices.getchoiceid(super().GetValue())
            if value == "" or value == "{}":
                value = None
            return value

    class clsListCtrl(wx.ListCtrl, clsFieldExtra):
        def __init__(self, parent, controldesc):

            super().init_field(parent, controldesc)

            controldescription = self.CONTROLDESCRIPTION.copy()

            # combobox preproces
            choices = self.choices.Load_Choices(controldescription)
            if choices != None:
                controldescription.update({"choices": choices})

            controldescription["style"] = wx.LC_REPORT

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(controldescription)
            )

            self.InsertColumn(
                0,
                controldescription["label"],
                wx.LIST_FORMAT_LEFT,
                controldescription["size"][0],
            )
            if "choices" in controldescription:
                for i in range(0, len(controldescription["choices"])):
                    self.InsertItem(i, controldescription["choices"][i])

            self.SetNormalColor()

            # clsListCtrl postprocess

        def SetValue(self, value):

            #   clear all the selections
            for item in range(self.GetItemCount()):
                self.SetItemState(item, 0, wx.LIST_STATE_SELECTED)

            #   Set selections
            if value != None:
                for val in value:
                    for item in range(self.GetItemCount()):
                        if val == self.GetItemText(item):
                            self.SetItemState(
                                item, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED
                            )

        def GetValue(self):
            selecteditems = []
            item = -1
            while 1:
                item = self.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                if item == -1:
                    break
                selecteditems.append(self.GetItemText(item))
            if selecteditems == []:
                return None
            return selecteditems

    class clsListCtrlID(wx.ListCtrl, clsFieldExtra):
        def __init__(self, parent, controldesc):

            super().init_field(parent, controldesc)

            controldescription = self.CONTROLDESCRIPTION.copy()

            # combobox preproces
            choices = self.choices.Load_Choices(controldescription)
            if choices != None:
                controldescription.update({"choices": choices})

            controldescription["style"] = wx.LC_REPORT

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(controldescription)
            )

            self.InsertColumn(
                0,
                controldescription["label"],
                wx.LIST_FORMAT_LEFT,
                controldescription["size"][0],
            )
            if "choices" in controldescription:
                for i in range(0, len(controldescription["choices"])):
                    self.InsertItem(i, controldescription["choices"][i])

            self.SetNormalColor()

            # clsListCtrl postprocess

        def SetValue(self, value):

            #   clear all the selections
            for item in range(self.GetItemCount()):
                self.SetItemState(item, 0, wx.LIST_STATE_SELECTED)

            #   Set the Selections
            if value != None:
                for val in value:
                    lookupval = self.choices.getchoicedisplay(int(val))
                    for item in range(self.GetItemCount()):
                        if lookupval == self.GetItemText(item):
                            self.SetItemState(
                                item, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED
                            )

        def GetValue(self):
            selecteditems = []
            item = -1
            while 1:
                item = self.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                if item == -1:
                    break
                selecteditems.append(
                    str(self.choices.getchoiceid(self.GetItemText(item)))
                )
            if selecteditems == []:
                return None
            return selecteditems

    class clsCheckBox(wx.CheckBox, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # checkbox preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )
            self.SetNormalColor()

            # checkbox postprocess

        def SetValue(self, value):
            if (value == True) or (value == 1):
                super().SetValue(wx.CHK_CHECKED)
            else:
                super().SetValue(wx.CHK_UNCHECKED)

        def GetValue(self):
            return super().IsChecked()

    class clsCheckListBox(wx.CheckListBox, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # checklistbox preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )
            self.SetNormalColor()

            # checklistbox postprocess

        def SetValue(self, value):
            self.Clear()
            checklist = {}
            if value != None:
                checklist = json.loads(value)
                try:
                    self.InsertItems(list(checklist.keys()), 0)
                except:
                    checklist = {}

            for check in checklist:
                if checklist[check] == "True":
                    self.Check(self.FindString(check), True)
                else:
                    self.Check(self.FindString(check), False)

        def GetValue(self):
            checklist = super().GetStrings()
            checked = super().GetCheckedStrings()
            di = {}
            for c in checklist:
                if c in checked:
                    di.update({c: "True"})
                else:
                    di.update({c: "False"})
            if di == {}:
                return None
            return json.dumps(di)

    class clsButton(wx.Button, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            if "id" in controldescription:
                id = controldescription["id"]
                controldescription.pop("id")
            else:
                id = wx.ID_ANY

            super().__init__(
                parent.PARENT.FORM, id, **getcontrolparameters(self.CONTROLDESCRIPTION)
            )

    class clsDataListViewCtrl(wx.dataview.DataViewListCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # preprocess

            self.DLVCrecords = clsDB.clsRecord(
                self.DBConnection, self.CONTROLDESCRIPTION["table"]
            )

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )
            self.SetNormalColor()

            # postprocess

            self.columnnames = []
            for i in range(len(self.CONTROLDESCRIPTION["column"])):
                self.AppendTextColumn(
                    label=self.CONTROLDESCRIPTION["column"][i]["label"],
                    width=self.CONTROLDESCRIPTION["column"][i]["width"],
                )
                self.columnnames.append(self.CONTROLDESCRIPTION["column"][i]["name"])

        def GetColumnNames(self):
            return self.columnnames

        def SetValueTable(self, parentrecord=None, table=None):
            self.rowID = []

            self.parent.FIELD.DeleteAllItems()

            if table == None:
                table = self.CONTROLDESCRIPTION["table"]

            self.DLVCrecords.load_records(table, parentrecord)
            for rec in self.DLVCrecords._record:
                self.AppendTableRecord(rec)
            self.SelectRow(0)

        def AppendTableRecord(self, record):
            columnsforcontrol = []
            for column in self.columnnames:
                for i in range(len(self.CONTROLDESCRIPTION["column"])):
                    if column == self.CONTROLDESCRIPTION["column"][i]["name"]:
                        if "lookup" in self.CONTROLDESCRIPTION["column"][i]:
                            columnsforcontrol.append(
                                str(
                                    self._choicesID2display(
                                        record[column],
                                        self.CONTROLDESCRIPTION["column"][i]["lookup"],
                                    )
                                )
                            )
                        else:
                            columnsforcontrol.append(str(record[column]))
                        break
            super().AppendItem(columnsforcontrol)

        def SetValueRecord(self, row, record):
            column = 0
            for field in record:
                super().SetValue(record[field], row, column)
                column = column + 1

        def GetSelectedRowID(self):
            return super().GetSelectedRow()

        def GetSelectedRow(self):
            selectedrow = super().GetSelectedRow()
            if selectedrow == wx.NOT_FOUND:
                return None
            return self.DLVCrecords._record[selectedrow]

        def _choicesID2display(self, value, table=None):
            """
            this module scans the lookup query for the choice indicated by "value"

            JSON values

            """
            global CONFIG

            if value == None:
                return None
            choice = value

            if table == None:
                if "lookup" in self.CONTROLDESCRIPTION:
                    table = self.CONTROLDESCRIPTION["lookup"]
                else:
                    return choice

            sql = "SELECT {field} FROM {table} WHERE ID = {key};".format(
                field=table["display"],
                table=table["table"],
                key=value,
            )
            cursor = self.DBConnection.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
            choice = ""
            self.subfields = []
            for i in range(len(row)):
                f = row[i]
                if type(f) is datetime.datetime:
                    f = f.strftime(CONFIG.get_Config_Value("Format", "DateTime"))
                self.subfields.append(f)
                choice = choice + str(f) + " "
            return choice

        def _choicesdisplay2ID(self, value, table=None):
            """
            this module scans the choices query for the given value and returns the "choice" based on "value"

            JSON values

            """
            choice = value
            if table == None:
                if "lookup" in self.CONTROLDESCRIPTION:
                    table = self.CONTROLDESCRIPTION["lookup"]
                else:
                    return choice

            sql = "SELECT {key} FROM {table} WHERE {display} = '{field}';".format(
                key=table["key"],
                table=table["table"],
                display=table["display"],
                field=value,
            )
            # sql = SQL.select()
            cursor = self.DBConnection.cursor(buffered=True)
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
            if row is None:
                return choice
            return row[0]

    class clsDateTime(wx.TextCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # Datetime preprocess

            # process date and time accourding to controldescription fields
            # "displaydate" & "displaytime"
            self.lc = self.CONTROLDESCRIPTION

            sz = self.lc["size"][0]
            self.lc["size"][0] = sz - 120
            self.datefield = clsField.clsDatePickerCtrl(parent, self.CONTROLDESCRIPTION)

            self.lc["pos"][0] = self.lc["pos"][0] + self.lc["size"][0]
            self.lc["size"][0] = sz - self.lc["size"][0]
            self.timefield = clsField.clsTimePickerCtrl(parent, self.CONTROLDESCRIPTION)

        def Disable(self):
            self.datefield.Disable()
            self.timefield.Disable()

        def SetValue(self, value):
            global CONFIG

            if value is not None:
                dtfmt = CONFIG.get_Config_Value("Format", "DateTime")
                self.datefield.SetValue(value, dtfmt)
                self.timefield.SetValue(value, dtfmt)

        def GetValue(self):
            global CONFIG

            dt = self.datefield.GetValue()
            tm = self.timefield.GetValue()
            return dt + " " + tm

        def SetWarningColor(self):
            self.datefield.SetBackgroundColour(FORMColors["Warning"]["bcolor"])
            self.datefield.SetForegroundColour(FORMColors["Warning"]["fcolor"])
            self.timefield.SetBackgroundColour(FORMColors["Warning"]["bcolor"])
            self.timefield.SetForegroundColour(FORMColors["Warning"]["fcolor"])

        def SetNormalColor(self):
            self.datefield.SetBackgroundColour(FORMColors["Normal"]["bcolor"])
            self.datefield.SetForegroundColour(FORMColors["Normal"]["fcolor"])
            # self.timefield.SetForegroundColour(fcolor)    # not supported on all platforms

    class clsDatePickerCtrl(wx.adv.DatePickerCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)
            controldescription = self.CONTROLDESCRIPTION.copy()

            # datepicker preprocess
            controldescription["style"] = wx.adv.DP_DROPDOWN

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(controldescription)
            )
            self.SetNormalColor()

            # DatePicker postprocess

        def SetValue(self, value, dateformat=None):
            if value == None:
                value = datetime.datetime.now().date()
            try:
                if dateformat is not None:
                    value = datetime.datetime.strptime(value, dateformat)
                else:
                    value = datetime.datetime.strptime(
                        value, CONFIG.get_Config_Value("Format", "Date")
                    )
            except Exception as Err:
                clsError.ErrorHandler.msg("clsFields:clsDatePickerCtrl:SetValue", Err)
            super().SetValue(value)

        def GetValue(self):
            return super().GetValue().Format(CONFIG.get_Config_Value("Format", "Date"))

    class clsTimePickerCtrl(wx.adv.TimePickerCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # timepicker preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )
            self.SetNormalColor()

            # timepicker postprocess

        def SetValue(self, value, timeformat=None):
            if value == None:
                return
                # value = datetime.datetime.now().time()
            try:
                if timeformat is not None:
                    value = datetime.datetime.strptime(value, timeformat)
                else:
                    value = datetime.datetime.strptime(
                        value, CONFIG.get_Config_Value("Format", "Time")
                    )
            except Exception as Err:
                clsError.ErrorHandler.msg("clsFields:clsTimePickerCtrl:SetValue", Err)
            super().SetValue(value)

        def GetValue(self):
            return super().GetValue().Format(CONFIG.get_Config_Value("Format", "Time"))

    class clsFilePickerCtrl(wx.FilePickerCtrl, clsFieldExtra):
        def __init__(self, parent, controldescription):

            super().init_field(parent, controldescription)

            # filepickerctrl preprocess

            super().__init__(
                parent.PARENT.FORM,
                wx.ID_ANY,
                **getcontrolparameters(self.CONTROLDESCRIPTION)
            )

            # filepickerctrl postprocess

            self.SetInitialDirectory(
                CONFIG.get_Config_Value(
                    self.CONTROLDESCRIPTION["directory"][0],
                    self.CONTROLDESCRIPTION["directory"][1],
                )
            )

            self.SetNormalColor()

        def SetValue(self, value):
            filename = value
            if filename == None:
                super().SetPath("")
            else:
                filename = str(value)
                path = os.path.dirname(value)
                filename = os.path.splitext(os.path.basename(value))
                self.SetInitialDirectory(
                    CONFIG.get_Config_Value(
                        self.CONTROLDESCRIPTION["directory"][0],
                        self.CONTROLDESCRIPTION["directory"][1],
                    )
                )
                super().SetPath(filename[0] + filename[1])

        def GetValue(self):
            value = str(super().GetPath())
            if value == "":
                return None
            path = os.path.dirname(value)
            filename = os.path.splitext(os.path.basename(value))
            fn = path + "\\" + filename[0] + filename[1]
            return fn
