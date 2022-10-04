# !/usr/bin/env python3
#   CMFormDescriptions.py - Form Descriptions for Church Manager
#   Rev. Jonathan C. Watt
#   July 8, 2021

import wx
from wx.core import Point, Size, Choice, TE_MULTILINE
import clsValidators
import operator

#
#   Validator Classes
#
valNotNUll = clsValidators._validatorNotNull()
valLen5 = clsValidators._validatorLen5()
valDateAndNull = clsValidators._validatorDateAndNull()
valDateAndNotNull = clsValidators._validatorDateAndNotNull()
valDateMMDD = clsValidators._validatorDateMMDD()
valDateandTime = clsValidators._validatorDateandTime()
valOnlyNone = clsValidators._validatorOnlyNone()


#
#   Classes
#
class pos:
    #
    #   Interator for Line Position for Fields
    #
    def __init__(self, start=0, stop=1000, incr=30) -> None:
        self.start = start
        self.val = start
        self.stop = stop
        self.iter = incr

    def _checkoverflow(self):
        if self.val > self.stop:
            return "Iterator overflow."

    def nextline(
        self, incr=0
    ):  # inc is an additional amount to add for additional spacing above the line
        self.val += self.iter
        self.val += incr
        self._checkoverflow()
        return self.val

    def sameline(
        self, incr=0
    ):  # inc is an additional amount to add for additional spacing above the line
        self.val += incr
        self._checkoverflow()
        return self.val

    def skipline(
        self, lines=2
    ):  # skip a line (lines is number of lines to skip, 2 = 1 line)
        self.val += self.iter * lines
        self._checkoverflow()
        return self.val

    def reset(self, start=0, stop=1000, incr=30, inc=0):
        self.start = start
        self.stop = stop
        self.val = start + inc
        self.iter = incr
        self._checkoverflow()
        return start


# --------------------------------------------------------------------------------------------
#   Church Table Form
# --------------------------------------------------------------------------------------------
#
#   Church Form Description <frmChurchFORM>
#
frmChurchCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 75,
    "FieldHeight": 30,
}
FormLineNumber = pos(0, frmChurchCONST["FormHeight"], frmChurchCONST["FieldHeight"])

frmChurchFORM = {
    "type": "Frame",
    "title": "frmChurch: Church Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmChurchCONST["FormWidth"], frmChurchCONST["FormHeight"]),
    "name": "frmChurch",
    "tablename": "tblChurch",
    "SQL": "SELECT * FROM tblChurch ORDER BY Church;",
}

#
#   Church Form Controls <frmChurchCONTROLS>
#
frmChurchCONTROLS = {
    "lblChurch": {
        "label": "Church:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblChurch",
        "type": "StaticText",
    },
    "Church": {
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "Church",
        "type": "TextCtrl",
    },
    "lblAddress": {
        "label": "Address:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAddress:",
        "type": "StaticText",
    },
    "Address": {
        "value": "",
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "Address",
        "type": "TextCtrl",
    },
    "Address2": {
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.nextline()),
        "size": wx.Size(300, 30),
        "name": "Address2",
        "type": "TextCtrl",
    },
    "lblCity": {
        "label": "City:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
        "type": "StaticText",
    },
    "City": {
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "City",
        "type": "TextCtrl",
    },
    "lblState": {
        "label": "City:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
        "type": "StaticText",
    },
    "State": {
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "State",
        "type": "TextCtrl",
    },
    "lblZip": {
        "label": "Zip:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblZip:",
        "type": "StaticText",
    },
    "Zip": {
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valLen5,
        "name": "Zip",
        "type": "TextCtrl",
    },
    "lblNote": {
        "label": "Note:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
        "type": "StaticText",
    },
    "Note": {
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
        "type": "TextCtrl",
    },
}
