# !/usr/bin/env python3
# 	clsValidators.py  Validator Classes for clsForms
#   Description <TODO> add description
# 	Rev. Jonathan C. Watt
# 	July 8, 2021
from glob import glob
import wx
import datetime

from clsConfig import CONFIG


class _validatorNotNull(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        # Note that every validator must implement the Clone() method.
        return _validatorNotNull()

    def Validate(self, win):
        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        name = ctrl.GetName()
        if text == None:
            wx.MessageBox(name + " cannot be empty.", "Error")
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        # if len(text) == 0:
        #    wx.MessageBox(name + " cannot be empty.", "Error")
        #    ctrl.SetBackgroundColour("pink")
        #    ctrl.SetFocus()
        #    ctrl.Refresh()
        #    return False
        else:
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.


class _validatorLen5(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        # Note that every validator must implement the Clone() method.
        return _validatorLen5()

    def Validate(self, win):
        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        name = ctrl.GetName()
        if len(text) != 6 and text.isnumeric() == False:
            wx.MessageBox(name + " must be 5 numeric characters.", "Error")
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.


class _validatorDateAndNull(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        # Note that every validator must implement the Clone() method.
        return _validatorDateAndNull()

    def Validate(self, win):
        global CONFIG

        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        name = ctrl.GetName()
        if text == "":
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True
        try:
            dt = datetime.datetime.strptime(text, CONFIG.get_Config_Value("FormatDate"))
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True
        except:
            wx.MessageBox(
                name
                + " not a valid date "
                + CONFIG.get_Config_Value("FormatDate")
                + ".",
                "Error",
            )
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.


class _validatorDateAndNotNull(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        # Note that every validator must implement the Clone() method.
        return _validatorDateAndNotNull()

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.

    def Validate(self, win):
        global CONFIG

        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        name = ctrl.GetName()
        try:
            dt = datetime.datetime.strptime(text, CONFIG.get_Config_Value("FormatDate"))
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True
        except:
            wx.MessageBox(
                name
                + " not a valid date "
                + CONFIG.get_Config_Value("FormatDate")
                + ".",
                "Error",
            )
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.


class _validatorDateMMDD(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        return _validatorDateMMDD()

    def Validate(self, win):
        global CONFIG

        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        name = ctrl.GetName()
        try:
            dt = datetime.datetime.strptime(
                text, CONFIG.get_Config_Value("FormatMonthDay")
            )
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True
        except:
            wx.MessageBox(
                name
                + " not a valid Month and Day "
                + CONFIG.get_Config_Value("FormatMonthDay")
                + ".",
                "Error",
            )
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.


class _validatorDateMMDDAndNull(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        return _validatorDateMMDDAndNull()

    def validate(self, win):
        global CONFIG

        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        if text == "":
            return True
        name = ctrl.GetName()
        try:
            dt = datetime.datetime.strptime(
                text, CONFIG.get_Config_Value("FormatMonthDay")
            )
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True
        except:
            wx.MessageBox(
                name
                + " not a valid Month and Day "
                + CONFIG.get_Config_Value("FormatMonthDay")
                + ".",
                "Error",
            )
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.


class _validatorDateTime(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        return _validatorDateTime()

    def Validate(self, win):
        global CONFIG

        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        name = ctrl.GetName()
        try:
            dt = datetime.datetime.strptime(
                text, CONFIG.get_Config_Value("FormatDateTime")
            )
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True
        except:
            wx.MessageBox(
                name
                + " not a valid Date and Time "
                + CONFIG.get_Config_Value("FormatDateTime")
                + ".",
                "Error",
            )
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True


class _validatorOnlyNone(wx.Validator):
    # allows only "None" to be selected in a CheckListBox
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        return _validatorOnlyNone()

    def Validate(self, win):
        ctrl = self.GetWindow()
        name = ctrl.GetName()
        text = ctrl.GetCheckedStrings()
        if text.count("None") == 0:
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True
        elif len(text) > 1:
            wx.MessageBox(name + ": 'None' can only be by itself.", "Error")
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            bckrnd = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            ctrl.SetBackgroundColour(bckrnd)
            ctrl.Refresh()
            return True

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.


validatorNotNull = _validatorNotNull()
validatorLen5 = _validatorLen5()
validatorDateAndNull = _validatorDateAndNull()
validatorDateAndNotNull = _validatorDateAndNotNull()
validatorDateMMDD = _validatorDateMMDD()
validatorDateMMDDAndNull = _validatorDateMMDDAndNull()
validatorDateTime = _validatorDateTime()
validatorOnlyNone = _validatorOnlyNone()


def setvalidatorfield(validator):
    if validator == "NotNull":
        return validatorNotNull
    if validator == "Len5":
        return validatorLen5
    if validator == "DateAndNull":
        return validatorDateAndNull
    if validator == "DateAndNotNull":
        return validatorDateAndNotNull
    if validator == "DateMMDD":
        return validatorDateMMDD
    if validator == "DateMMDDAndNull":
        return validatorDateMMDDAndNull
    if validator == "DateTime":
        return validatorDateTime
    if validator == "OnlyNone":
        return validatorOnlyNone
