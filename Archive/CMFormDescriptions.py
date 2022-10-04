# !/usr/bin/env python3
#   CMFormDescriptions.py - Form Descriptions for Church Manager
#   Rev. Jonathan C. Watt
#   July 8, 2021

import wx
from wx.core import Point, Size, Choice, Colour, ColourDatabase, TE_MULTILINE
import clsValidators
import operator

FORMColors = {
    "Warning": {"fcolor": "White", "bcolor": "Red"},
    "Error": {"fcolor": "White", "bcolor": "Red"},
    "Notice": {"fcolor": "Blue", "bcolor": "White"},
    "Normal": {"fcolor": "Black", "bcolor": "White"},
}


def frmUpdateDescription(description, key, value):
    return {**description, **{key: value}}


def frmDeleteDescription(description, key):
    description.pop(key)
    return description


def frmGetFormDescription(form):
    if form == "frmHymnUsageDisplay":
        return frmHymnUsageDisplayFORM
    elif form == "frmHymnUsage":
        return frmHymnUsageFORM
    elif form == "frmPropers":
        return frmPropersFORM
    elif form == "frmReadingList":
        return frmReadingListFORM
    elif form == "frmAltReadingsDisplay":
        return frmAltReadingsDisplayFORM
    elif form == "frmReading":
        return frmReadingFORM
    elif form == "frmChurch":
        return frmChurchFORM
    elif form == "frmHymn":
        return frmHymnFORM
    elif form == "frmPropers":
        return frmPropersFORM
    elif form == "frmReading":
        return frmReadingFORM
    elif form == "frmService":
        return frmServiceFORM
    elif form == "frmAltReading":
        return frmAltReadingFORM
    elif form == "frmHymnUsage":
        return frmHymnUsageFORM
    elif form == "frmHymnSearch":
        return frmHymnSearchFORM


def frmGetControlDescription(form):
    if form == "frmHymnUsageDisplay":
        return frmHymnUsageDisplayCONTROLS
    elif form == "frmHymnUsage":
        return frmHymnUsageCONTROLS
    elif form == "frmPropers":
        return frmPropersCONTROLS
    elif form == "frmReadingList":
        return frmReadingListCONTROLS
    elif form == "frmAltReadingsDisplay":
        return frmAltReadingsDisplayCONTROLS
    elif form == "frmReading":
        return frmReadingCONTROLS
    elif form == "frmReading":
        return frmReadingCONTROLS
    elif form == "frmChurch":
        return frmChurchCONTROLS
    elif form == "frmHymn":
        return frmHymnCONTROLS
    elif form == "frmPropers":
        return frmPropersCONTROLS
    elif form == "frmReading":
        return frmReadingCONTROLS
    elif form == "frmService":
        return frmServiceCONTROLS
    elif form == "frmAltReading":
        return frmAltReadingCONTROLS
    elif form == "frmHymnUsage":
        return frmHymnUsageCONTROLS
    elif form == "frmHymnSearch":
        return frmHymnSearchCONTROLS


btnNavigationCONTROLS = {
    "Navigation": {
        "btnNew": {
            "type": "Button",
            "label": "Ne&w",
            "pos": wx.Point(0, 0),
            "size": wx.Size(50, 30),
            "name": "btnNew",
        },
        "btnUpdate": {
            "type": "Button",
            "label": "&Update",
            "pos": wx.Point(0, 0),
            "size": wx.Size(70, 30),
            "name": "btnUpdate",
        },
        "btnDelete": {
            "type": "Button",
            "label": "&Delete",
            "pos": wx.Point(0, 0),
            "size": wx.Size(70, 30),
            "name": "btnDelete",
        },
        "btnFirst": {
            "type": "Button",
            "label": "<<",
            "pos": (wx.Point(0, 0)),
            "size": wx.Size(40, 30),
            "name": "btnFirst",
        },
        "btnPrev": {
            "type": "Button",
            "label": "<",
            "pos": wx.Point(0, 0),
            "size": wx.Size(40, 30),
            "name": "btnPrev",
        },
        "btnNext": {
            "type": "Button",
            "label": ">",
            "pos": wx.Point(0, 0),
            "size": wx.Size(40, 30),
            "name": "btnNext",
        },
        "btnLast": {
            "type": "Button",
            "label": ">>",
            "pos": wx.Point(0, 0),
            "size": wx.Size(40, 30),
            "name": "btnLast",
        },
    },
    "Close": {
        "btnClose": {
            "type": "Button",
            "label": "&Close",
            "pos": wx.Point(0, 0),
            "name": "btnClose",
        },
    },
}

#
#   Standard Validator Classes
#
valNotNUll = clsValidators._validatorNotNull()
valLen5 = clsValidators._validatorLen5()
valDateAndNull = clsValidators._validatorDateAndNull()
valDateAndNotNull = clsValidators._validatorDateAndNotNull()
valDateMMDD = clsValidators._validatorDateMMDD()
valDateMMDDAndNull = clsValidators._validatorDateMMDDAndNull()
valDateandTime = clsValidators._validatorDateandTime()
valOnlyNone = clsValidators._validatorOnlyNone()
#
#   Other Classes
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

    def nextline(self, incr=0):  # incr is an additional amount to add for additional spacing above the line
        self.val += self.iter
        self.val += incr
        self._checkoverflow()
        return self.val

    def sameline(self, incr=0):  # incr is an additional amount to add for additional spacing above the line
        self.val += incr
        self._checkoverflow()
        return self.val

    def skipline(self, lines=2):  # skip a line (lines is number of lines to skip, 2 = 1 line)
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


#
#   FORM DESCRIPTION <frm<xxx>FORM> and FORM CONTROL DESCRIPTION <frm<xxx>CONTROLS>
#
#       wxPython Controls Currently implemented
#           'Frame' - wx.Frame()
#           'StaticText' - wx.StaticText()
#           'TextCtrl' - wx.TextCtrl()
#           'Button' - xw.Button()
#           'ComboBox' - xw.ComboBox()
#           'CheckBox' - wx.CheckBox()
#   <TODO> multi line field as in date lookups.
#           when "name" equals the following binding happen
#           'btnClose' - wx.Button(), bound to "on_close_click"
#           'btnNext' - wx.Button(), bound to "on_next_record_click"
#           'btnPrev' - wx.Button(), bound to "on_prev_record_click"
#           'btnNew' - wx.Button(), bound to "on_new_record_click"
#           'btnDelete' - wx.Button(), bound to "on_delete_record_click"
#
#       valid form parameters: (passed to wxPython)
#           'title'
#           'type' - "Frame"
#           'pos'
#           'size'
#           'name'
#           'style' - wxPython styles see wxPython documentation (not implemented for FORMS)
#
#       extra form parameters: (not passed to wxPython, implemente in clsForms class)
#          'tablename' - Name of the table
#           'SQL' - Default SQL for the form records
#
#       valid field parameters: (passed to appropriate wxPython)
#           'type' - see wxPython Controls Currently implemented above Standard Validator Classes
#           'pos'
#           'size'
#           'name'
#           'label'
#           'choices' - ComboBox Choices
#           'validator' - see clsValidtors.py and above.
#           'style' - wxPython styles see wxPython documentation
#           'value' - initial value of the field. (not implemented)
#
#       extra field parameters: (not passed to wxPython, implemente in clsForms class)
#           'choicesSQL' - Drop down choices from another table.
#           'lkpSQL' - Single field lookup from another table ('StaticText', 'TextCtrl')
#           'fcolor'- Foreground Color
#           'bcolor' - Background Color
#
#
#
#   UtilityForm Descrption
#
frmReportMainCONST = {
    "FieldHeight": 30,
    "FormColumn1": 20,
    "FormColumn2": 300,
    "FormHeight": 400,
    "FormWidth": 600,
}
FormLineNumber = pos(0, frmReportMainCONST["FormHeight"], frmReportMainCONST["FieldHeight"])
frmReportMainFORM = {
    "name": "frmReportMain",
    "pos": wx.Point(0, 0),
    "size": wx.Size(frmReportMainCONST["FormWidth"], frmReportMainCONST["FormHeight"]),
    "style": wx.CAPTION,
    "title": "Church Manager - Report (v0.1)",
    "type": "Frame",
}

frmReportMainCONTROLS = {
    "btnPropersDisplay": {
        "type": "Button",
        "label": "Display Propers",
        "pos": wx.Point(frmReportMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnPropersDisplay",
    },
    "btnClose": {
        "type": "Button",
        "label": "Close",
        "pos": wx.Point(
            frmReportMainCONST["FormWidth"] - 100,
            frmReportMainCONST["FormHeight"] - 100,
        ),
        "name": "btnClose",
    },
}

frmUtilityMainCONST = {
    "FormWidth": 600,
    "FormHeight": 400,
    "FormColumn1": 20,
    "FormColumn2": 300,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmUtilityMainCONST["FormHeight"], frmUtilityMainCONST["Fieldheight"])
frmUtilityMainFORM = {
    "type": "Frame",
    "pos": wx.Point(0, 0),
    "size": wx.Size(frmUtilityMainCONST["FormWidth"], frmUtilityMainCONST["FormHeight"]),
    "title": "Church Manager - Utility (v0.1)",
    "name": "frmUtilityMain",
    "style": wx.CAPTION,
}

frmUtilityMainCONTROLS = {
    "btnEditConfig": {
        "type": "Button",
        "label": "Add/Edit/Delete Configurations",
        "pos": wx.Point(frmUtilityMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnConfig",
    },
    "btnEditOption": {
        "type": "Button",
        "label": "Add/Edit/Delete Options",
        "pos": wx.Point(frmUtilityMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnOptions",
    },
    "btnEditChoices": {
        "type": "Button",
        "label": "Add/Edit/Delete Choices",
        "pos": wx.Point(frmUtilityMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnChoices",
    },
    "btnClose": {
        "type": "Button",
        "label": "Close",
        "pos": wx.Point(
            frmReportMainCONST["FormWidth"] - 100,
            frmReportMainCONST["FormHeight"] - 100,
        ),
        "name": "btnClose",
    },
}

#
#   Worship Form Descrption
#
frmWorshipMainCONST = {
    "FormWidth": 600,
    "FormHeight": 400,
    "FormColumn1": 20,
    "FormColumn2": 300,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmWorshipMainCONST["FormHeight"], frmWorshipMainCONST["Fieldheight"])

frmWorshipMainFORM = {
    "type": "Frame",
    "pos": wx.Point(50, 50),
    "size": wx.Size(frmWorshipMainCONST["FormWidth"], frmWorshipMainCONST["FormHeight"]),
    "title": "Church Manager - Worship (v0.1)",
    "name": "frmWorshipMain",
    "style": wx.CAPTION,
    "linkedform": {
        "frmChurch": {"bindbtn": "btnEditChurch", "controls": ["Close", "Navigation"]},
        "frmHymn": {"bindbtn": "btnEditHymn", "controls": ["Close", "Navigation"]},
        "frmPropers": {"bindbtn": "btnEditPropers", "controls": ["Close", "Navigation"]},
        "frmReading": {"bindbtn": "btnEditReading", "controls": ["Close", "Navigation"]},
        "frmService": {"bindbtn": "btnEditService", "controls": ["Close", "Navigation"]},
        "frmAltReading": {"bindbtn": "btnEditAltReading", "controls": ["Close", "Navigation"]},
        "frmHymnUsage": {"bindbtn": "btnEditHymnUsage", "controls": ["Close", "Navigation"]},
        "frmHymnUsageDisplay": {"bindbtn": "btnEditHymnUsagebyService", "controls": ["Close", "Navigation"]},
    },
}

frmWorshipMainCONTROLS = {
    "btnEditChurch": {
        "type": "Button",
        "label": "Add/Edit/Delete Church",
        "pos": wx.Point(frmWorshipMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnEditChurch",
    },
    "btnEditHymn": {
        "type": "Button",
        "label": "Add/Edit/Delete Hymn",
        "pos": wx.Point(frmWorshipMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnEditHymn",
    },
    "btnEditPropers": {
        "type": "Button",
        "label": "Add/Edit/Delete Propers",
        "pos": wx.Point(frmWorshipMainCONST["FormColumn1"], FormLineNumber.skipline()),
        "name": "btnEditPropers",
    },
    "btnEditReading": {
        "type": "Button",
        "label": "Add/Edit/Delete Reading",
        "pos": wx.Point(frmWorshipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
        "name": "btnEditReading",
    },
    "btnEditService": {
        "type": "Button",
        "label": "Add/Edit/Delete Service",
        "pos": wx.Point(frmWorshipMainCONST["FormColumn2"], FormLineNumber.reset(120)),
        "name": "btnEditService",
    },
    "btnEditAltReading": {
        "type": "Button",
        "label": "Add/Edit/Delete Alternate Reading",
        "pos": wx.Point(frmWorshipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditAltReading",
    },
    "btnEditHymnUsage": {
        "type": "Button",
        "label": "Add/Edit/Delete Hymn Usage",
        "pos": wx.Point(frmWorshipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditHymnUsage",
    },
    "btnEditHymnUsagebyService": {
        "type": "Button",
        "label": "Hymn Usage by Service",
        "pos": wx.Point(frmWorshipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
    },
}

#
# Membership Form Description
#
frmMembershipMainCONST = {
    "FormWidth": 600,
    "FormHeight": 500,
    "FormColumn1": 10,
    "FormColumn2": 300,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmMembershipMainCONST["FormHeight"], frmMembershipMainCONST["Fieldheight"])
frmMembershipMainFORM = {
    "type": "Frame",
    "pos": wx.Point(0, 0),
    "size": wx.Size(frmMembershipMainCONST["FormWidth"], frmMembershipMainCONST["FormHeight"]),
    "title": "Church Manager - Membership (v0.1)",
    "name": "frmMembershipMain",
    "style": wx.CAPTION,
}
frmMembershipMainCONTROLS = {
    "btnEditChurch": {
        "type": "Button",
        "label": "Add/Edit/Delete Church",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn1"], FormLineNumber.nextline()),
        # 'size': wx.Size(0, 0),
        "name": "btnEditChurch",
    },
    "btnEditPerson": {
        "type": "Button",
        "label": "Add/EditDelete Person",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn1"], FormLineNumber.skipline()),
        "name": "btnEditPerson",
    },
    "btnEditPersonAddress": {
        "type": "Button",
        "label": "Add/Edit/Delete Person Address",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
        "name": "btnEditPersonAddress",
    },
    "btnEditPersonContact": {
        "type": "Button",
        "label": "Add/Edit/Delete Person Contact",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
        "name": "btnEditPersonContact",
    },
    "btnEditPersonDate": {
        "type": "Button",
        "label": "Add/Edit/Delete Person Date",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
        "name": "btnEditPersonDate",
    },
    "btnEditPersonDateGrid": {
        "type": "Button",
        "label": "Person Date Grid",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
        "name": "btnEditPersonDateGrid",
    },
    "btnEditFamily": {
        "type": "Button",
        "label": "Add/Edit/Delete Family",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn2"], FormLineNumber.reset(105)),
        "name": "btnEditFamily",
    },
    "btnEditFamilyAddress": {
        "type": "Button",
        "label": "Add/Edit/Delete Family Address",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditFamilyAddress",
    },
    "btnEditFamilyContact": {
        "type": "Button",
        "label": "Add/Edit/Delete Family Contact",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditFamilyContact",
    },
    "btnEditFamilyDate": {
        "type": "Button",
        "label": "Add/Edit/Delete Family Date",
        "pos": wx.Point(frmMembershipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditFamilyDate",
    },
    "btnClose": {
        "type": "Button",
        "label": "Close",
        "pos": wx.Point(
            frmMembershipMainCONST["FormWidth"] - 100,
            frmMembershipMainCONST["FormHeight"] - 100,
        ),
        "name": "btnClose",
    },
}

#
#   ProjectMain Form Description
#
frmProjectMainCONST = {
    "FormWidth": 600,
    "FormHeight": 350,
    "FormColumn1": 25,
    "FormColumn2": 300,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmProjectMainCONST["FormHeight"], frmProjectMainCONST["Fieldheight"])
frmProjectMainFORM = {
    "type": "Frame",
    "pos": wx.Point(0, 0),
    "size": wx.Size(frmProjectMainCONST["FormWidth"], frmProjectMainCONST["FormHeight"]),
    "title": "Church Manager - ProjectMain (v0.1)",
    "name": "frmProjectMain",
    "style": wx.CAPTION,
}
frmProjectMainCONTROLS = {
    "btnEditChurch": {
        "type": "Button",
        "label": "Add/Edit/Delete Church",
        "pos": wx.Point(frmProjectMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnEditChurch",
    },
    "btnEditPerson": {
        "type": "Button",
        "label": "Add/EditDelete Person",
        "pos": wx.Point(frmProjectMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnEditPerson",
    },
    "btnEditSkill": {
        "type": "Button",
        "label": "Add/Edit/Delete Skill",
        "pos": wx.Point(frmProjectMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnEditSkill",
    },
    "btnEditProject": {
        "type": "Button",
        "label": "Add/Edit/Delete Project",
        "pos": wx.Point(frmProjectMainCONST["FormColumn2"], FormLineNumber.reset(105)),
        "name": "btnEditProject",
    },
    "btnEditProjectTask": {
        "type": "Button",
        "label": "Add/Edit/Delete Project Task",
        "pos": wx.Point(frmProjectMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditProjectTask",
    },
    "btnEditProjectSkill": {
        "type": "Button",
        "label": "Add/Edit/Delete Project Skill",
        "pos": wx.Point(frmProjectMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditProjectSkill",
    },
    "btnClose": {
        "type": "Button",
        "label": "Close",
        "pos": wx.Point(
            frmProjectMainCONST["FormWidth"] - 100,
            frmProjectMainCONST["FormHeight"] - 100,
        ),
        "name": "btnClose",
    },
}

#
#   AttendanceMain
#
frmAttendanceMainCONST = {
    "FormWidth": 600,
    "FormHeight": 350,
    "FormColumn1": 25,
    "FormColumn2": 300,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmAttendanceMainCONST["FormHeight"], frmAttendanceMainCONST["Fieldheight"])

frmAttendanceMainFORM = {
    "type": "Frame",
    "pos": wx.Point(0, 0),
    "size": wx.Size(frmAttendanceMainCONST["FormWidth"], frmAttendanceMainCONST["FormHeight"]),
    "title": "Church Manager - ProjectMain (v0.1)",
    "name": "frmAttendanceMain",
    "style": wx.CAPTION,
}

frmAttendanceMainCONTROLS = {
    "btnEditChurch": {
        "type": "Button",
        "label": "Add/Edit/Delete Church",
        "pos": wx.Point(frmAttendanceMainCONST["FormColumn1"], FormLineNumber.nextline()),
        # 'size': wx.Size(0, 0),
        "name": "btnEditChurch",
    },
    "btnEditPerson": {
        "type": "Button",
        "label": "Add/EditDelete Person",
        "pos": wx.Point(frmAttendanceMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnEditPerson",
    },
    "btnEditService": {
        "type": "Button",
        "label": "Add/EditDelete Service",
        "pos": wx.Point(frmAttendanceMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnEditService",
    },
    "btnEditAttendance": {
        "type": "Button",
        "label": "Add/EditDelete Attendance",
        "pos": wx.Point(frmAttendanceMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnEditAttendance",
    },
    "btnClose": {
        "type": "Button",
        "label": "Close",
        "pos": wx.Point(
            frmAttendanceMainCONST["FormWidth"] - 100,
            frmAttendanceMainCONST["FormHeight"] - 100,
        ),
        "name": "btnClose",
    },
}

frmConfigCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 75,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmConfigCONST["FormHeight"], frmConfigCONST["Fieldheight"])
frmConfigFORM = {
    "type": "Frame",
    "title": "frmConfig: Config Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmConfigCONST["FormWidth"], frmConfigCONST["FormHeight"]),
    "name": "frmConfig",
    "tablename": "tblConfig",
    "SQL": "SELECT * FROM tblConfig;",
    "style": wx.CAPTION,
}
frmConfigCONTROLS = {
    "lblConfigType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": wx.Point(frmConfigCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblConfigType",
    },
    "ConfigType": {
        "type": "ComboBox",
        "pos": wx.Point(frmConfigCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ConfigType';",
        "choicevalue": 0,
        "style": wx.CB_READONLY,
        "name": "ConfigType",
    },
    "lblConfigValue": {
        "type": "StaticText",
        "label": "Value:",
        "pos": wx.Point(frmConfigCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblConfigValue",
    },
    "ConfigValue": {
        "type": "TextCtrl",
        "pos": wx.Point(frmConfigCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "ConfigValue",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmConfigCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmConfigCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}

#
#   Church Table Form
#
frmChurchCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 75,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmChurchCONST["FormHeight"], frmChurchCONST["Fieldheight"])
frmChurchFORM = {
    "type": "Frame",
    "title": "frmChurch: Church Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmChurchCONST["FormWidth"], frmChurchCONST["FormHeight"]),
    "name": "frmChurch",
    "tablename": "tblChurch",
    "SQL": "SELECT * FROM tblChurch ORDER BY Church;",
    "style": wx.CAPTION,
}
frmChurchCONTROLS = {
    "lblChurch": {
        "type": "StaticText",
        "label": "Church:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblChurch",
        "bindmouse": wx.EVT_LEFT_DCLICK,
    },
    "Church": {
        "type": "TextCtrl",
        "value": "",
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "Church",
    },
    "lblAddress": {
        "type": "StaticText",
        "label": "Address:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAddress:",
    },
    "Address": {
        "type": "TextCtrl",
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "Address",
    },
    "Address2": {
        "type": "TextCtrl",
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.nextline()),
        "size": wx.Size(300, 30),
        "name": "Address2",
    },
    "lblCity": {
        "type": "StaticText",
        "label": "City:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "City": {
        "type": "TextCtrl",
        "value": "",
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "City",
    },
    "lblState": {
        "type": "StaticText",
        "label": "State:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "State": {
        "type": "TextCtrl",
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "State",
    },
    "lblZip": {
        "type": "StaticText",
        "label": "Zip:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblZip:",
    },
    "Zip": {
        "type": "TextCtrl",
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valLen5,
        "name": "Zip",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}

#
#   Hymn Table Form
#
frmHymnCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 80,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmHymnCONST["FormHeight"], frmHymnCONST["Fieldheight"])

frmHymnFORM = {
    "type": "Frame",
    "title": "frmHymn: Hymn Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmHymnCONST["FormWidth"], frmHymnCONST["FormHeight"]),
    # 'style': 'test',
    "name": "frmHymn",
    "tablename": "tblHymn",
    "SQL": "SELECT * FROM tblHymn ORDER BY Hymn;",
    "style": wx.CAPTION,
}
frmHymnCONTROLS = {
    "lblHymnal": {
        "type": "StaticText",
        "label": "Hymnal:",
        "pos": wx.Point(frmHymnCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblHymnal",
    },
    "HymnalID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Hymnal FROM tblHymnal;",
        "choicevalue": 0,
        "comparevalue": 0,
        "lkpSQL": "SELECT Hymnal FROM tblHymnal WHERE ID = {value};",
        "pos": wx.Point(frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "HymnalID",
    },
    "lblHymn": {
        "type": "StaticText",
        "label": "Hymn:",
        "pos": wx.Point(frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblHymnalID",
    },
    "Hymn": {
        "type": "TextCtrl",
        "pos": wx.Point(frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Hymn",
    },
    "lblTitle": {
        "type": "StaticText",
        "label": "Title:",
        "pos": wx.Point(frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblTitle",
    },
    "Title": {
        "type": "TextCtrl",
        "pos": wx.Point(frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Title",
    },
    "lblBibleText": {
        "type": "StaticText",
        "label": "Bible Refs:",
        "pos": wx.Point(frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblBitleText",
    },
    "BibleText": {
        "type": "TextCtrl",
        "pos": wx.Point(frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "BibleText",
    },
    "lblCategory": {
        "type": "StaticText",
        "label": "Category:",
        "pos": wx.Point(frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCategory",
    },
    "Category": {
        "type": "ComboBox",
        "pos": wx.Point(frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Category",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Category';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}

#
#   Hymn Usage Table Form
#
frmHymnUsageCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 150,
    "Fieldheight": 30,
    "FieldPos": pos(0, 400, 30),  # (formheight, fieldheight)
}
FormLineNumber = pos(0, frmHymnUsageCONST["FormHeight"], frmHymnUsageCONST["Fieldheight"])
frmHymnUsageFORM = {
    "type": "Frame",
    "title": "frmHymnUsage: Hymn Usage Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmHymnUsageCONST["FormWidth"], frmHymnUsageCONST["FormHeight"]),
    "name": "frmHymnUsage",
    "tablename": "tblHymnUsage",
    "SQL": "SELECT * FROM tblHymnUsage ORDER BY ServiceID;",
    "style": wx.CAPTION,
}
frmHymnUsageCONTROLS = {
    "lblServiceID": {
        "type": "StaticText",
        "label": "Service Date/Time:",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblServiceID",
    },
    "ServiceID": {
        "type": "TextCtrl",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "ServiceID",
        "lkpSQL": "SELECT DateTime FROM tblService WHERE ID = {value}",
        "fcolor": FORMColors["Notice"]["fcolor"],
        "bcolor": FORMColors["Notice"]["bcolor"],
        "readonly": True,
    },
    "lblHymnID": {
        "type": "StaticText",
        "label": "Hymn:",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblHymnID",
    },
    "HymnID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT h.ID,concat(hl.HymnalPrefix, h.Hymn, ' ', h.Title) FROM tblHymnal hl JOIN tblHymn h ON h.HymnalID = hl.ID",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT concat(hl.HymnalPrefix, h.Hymn, ' ', h.Title) FROM tblHymnal hl JOIN tblHymn h ON h.HymnalID = hl.ID WHERE h.ID = {value};",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "HymnID",
    },
    "lblHymnUsageTypeID": {
        "type": "StaticText",
        "label": "Hymn Usage Type ID:",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblHymnUsageTypeID",
    },
    "HymnUsageTypeID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, UsedAs FROM tblHymnUsageType;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT UsedAs FROM tblHymnUsageType WHERE ID = {value};",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "HymnUsageTypeID",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}

#
#   Propers Table Form
#
frmPropersCONST = {
    "FormWidth": 620,
    "FormHeight": 450,
    "FormButtonRow": 450 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "FormColumn3": 500,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmPropersCONST["FormHeight"], frmPropersCONST["Fieldheight"])

frmPropersFORM = {
    "type": "Frame",
    "title": "frmPropers: Propers Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmPropersCONST["FormWidth"], frmPropersCONST["FormHeight"]),
    "name": "frmPropers",
    "tablename": "tblPropers",
    "SQL": "SELECT Lectionary,Sort,Series,Season,LiturgicalDate,CalendarDateFrom,CalendarDateTo,Color FROM tblPropers ORDER BY Sort;",
    "style": wx.CAPTION,
    "linkedform": {
        "frmReading": {
            "SQL": "SELECT * FROM tblReading WHERE PropersID = {ID};",
            "pos": wx.Point(frmPropersCONST["FormWidth"] + 20, 10),
            "controls": ["Close", "Navigation"],
            "bindbtn": "btnEditReading",
        }
    },
}
frmPropersCONTROLS = {
    "lblLectionary": {
        "type": "StaticText",
        "label": "Lectionary:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblLectionary",
    },
    "Lectionary": {
        "type": "ComboBox",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Lectionary';",
        "choicevalue": 0,
        "comparevalue": 0,
        "name": "Lectionary",
    },
    "lblSort": {
        "type": "StaticText",
        "label": "Sort:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSort",
    },
    "Sort": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Sort",
        # 'validator' : valNumeric, <TODO> Not yet implemented.
    },
    "lblSeries": {
        "type": "StaticText",
        "label": "Series:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSeires",
    },
    "Series": {
        "type": "ComboBox",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Series",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Series';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblSeason": {
        "type": "StaticText",
        "label": "Season:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSeason",
    },
    "Season": {
        "type": "ComboBox",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "Season",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Season';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblLiturgicalDate": {
        "type": "StaticText",
        "label": "Liturgical Date:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLiturgicalDate",
    },
    "LiturgicalDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "LiturgicalDate",
        # "validator": valNotNUll,
    },
    "btnEditReading": {
        "type": "Button",
        "label": "Readings",
        "pos": wx.Point(frmPropersCONST["FormColumn3"], FormLineNumber.sameline()),
        "name": "btnEditReading",
    },
    "lblCalendarDateFrom": {
        "type": "StaticText",
        "label": "From:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCalendarDateFrom",
    },
    "CalendarDateFrom": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "CalendarDateFrom",
        "validator": valDateMMDDAndNull,  # <TODO> This validator isn't being called by wxPython
    },
    "lblCalendarDateTo": {
        "type": "StaticText",
        "label": "To:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCalendarDateTo",
    },
    "CalendarDateTo": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "CalendarDateTo",
        "validator": valDateMMDDAndNull,  # <TODO> This validator isn't being called by wxPython
    },
    "lblColor": {
        "type": "StaticText",
        "label": "Liturgical Color:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblColor",
    },
    "Color": {
        "type": "ComboBox",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Color",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Color';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblAltColor": {
        "type": "StaticText",
        "label": "Alt Color:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAltColor",
    },
    "AltColor": {
        "type": "ComboBox",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "AltColor",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Color';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
    },
}
# --
#
#   Readings Table Form
#
frmReadingCONST = {
    "FormWidth": 620,
    "FormHeight": 450,
    "FormButtonRow": 450 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmReadingCONST["FormHeight"], frmReadingCONST["Fieldheight"])

frmReadingFORM = {
    "type": "Frame",
    "title": "frmReading: Reading Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmReadingCONST["FormWidth"], frmReadingCONST["FormHeight"]),
    "name": "frmReading",
    "tablename": "tblReading",
    "SQL": "SELECT * FROM tblReading ORDER BY PropersID;",
    "style": wx.CAPTION,
}

frmReadingCONTROLS = {
    "plabels": {
        "type": "StaticText",
        "label": "            Yr Season Proper",  # <TODO> Yuck!
        "pos": wx.Point(frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "name": "plabel",
    },
    "lblPropersID": {
        "type": "StaticText",
        "label": "Propers:",
        "pos": wx.Point(frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblPropersID",
    },
    "PropersID": {
        "type": "TextCtrl",
        "pos": wx.Point(frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "PropersID",
        "lkpSQL": "SELECT CONCAT( Series,' ',Season,' ',LiturgicalDate) FROM tblPropers WHERE ID = {value}",
        "readonly": True,
    },
    "lblReading": {
        "type": "StaticText",
        "label": "Reading:",
        "pos": wx.Point(frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblReading",
    },
    "Reading": {
        "type": "ComboBox",
        "pos": wx.Point(frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Reading",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Reading';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblReadingReference": {
        "type": "StaticText",
        "label": "Reference:",
        "pos": wx.Point(frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblReadingReference",
    },
    "ReadingReference": {
        "type": "TextCtrl",
        "pos": wx.Point(frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "ReadingReference",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note",
        "pos": wx.Point(frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
    },
}

#
#   Alternate Readings Table Form
#
frmReadingCONST = {
    "FormWidth": 620,
    "FormHeight": 450,
    "FormButtonRow": 450 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmReadingCONST["FormHeight"], frmReadingCONST["Fieldheight"])

frmReadingFORM = {
    "type": "Frame",
    "title": "frmReading: Reading Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmReadingCONST["FormWidth"], frmReadingCONST["FormHeight"]),
    "name": "frmReading",
    "tablename": "tblReading",
    "SQL": "SELECT * FROM tblReading ORDER BY PropersID;",
    "style": wx.CAPTION,
}

frmReadingCONTROLS = {
    "plabels": {
        "type": "StaticText",
        "label": "            Yr Season Proper",  # <TODO> Yuck!
        "pos": wx.Point(frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "name": "plabel",
    },
    "lblPropersID": {
        "type": "StaticText",
        "label": "Propers:",
        "pos": wx.Point(frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblPropersID",
    },
    "PropersID": {
        "type": "TextCtrl",
        "pos": wx.Point(frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "PropersID",
        "lkpSQL": "SELECT CONCAT( Series,' ',Season,' ',LiturgicalDate) FROM tblPropers WHERE ID = {value}",
        "readonly": True,
    },
    "lblReading": {
        "type": "StaticText",
        "label": "Reading:",
        "pos": wx.Point(frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblReading",
    },
    "Reading": {
        "type": "ComboBox",
        "pos": wx.Point(frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Reading",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Reading';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblReadingReference": {
        "type": "StaticText",
        "label": "Reference:",
        "pos": wx.Point(frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblReadingReference",
    },
    "ReadingReference": {
        "type": "TextCtrl",
        "pos": wx.Point(frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "ReadingReference",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note",
        "pos": wx.Point(frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
    },
}


#
#   Person Table Form
#
frmPersonCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
    "FieldPos": pos(0, 525, 30),
}
FormLineNumber = pos(0, frmPersonCONST["FormHeight"], frmPersonCONST["Fieldheight"])

frmPersonFORM = {
    "type": "Frame",
    "title": "frmPerson : Person Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmPersonCONST["FormWidth"], frmPersonCONST["FormHeight"]),
    "name": "frmPerson",
    "tablename": "tblPerson",
    "SQL": "SELECT ID,ChurchID,FamilyID,FirstName,MiddleName,LastName,Status,Baptized,Confirmed,Member,AssociateMember,Picture, Note FROM tblPerson ORDER BY LastName",
    "style": wx.CAPTION,
}
frmPersonCONTROLS = {
    "lblChurchID": {
        "type": "StaticText",
        "label": "Church:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblChurchID",
    },
    "ChurchID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Church FROM tblChurch;",
        "choicevalue": 0,
        "lkpSQL": "SELECT Church FROM tblChurch WHERE ID = {value};",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "ChurchID",
    },
    "lblFamilyID": {
        "type": "StaticText",
        "label": "Family:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblFamilyID",
    },
    "FamilyID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, FamilyName FROM tblFamily;",
        "choicevalue": 0,
        "lkpSQL": "SELECT FamilyName FROM tblFamily WHERE ID = {value};",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "FamilyID",
    },
    "lblFirstName": {
        "type": "StaticText",
        "label": "First Name:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblFirstName",
    },
    "FirstName": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "FirstName",
    },
    "lblMiddleName": {
        "type": "StaticText",
        "label": "Middle Name:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblMiddleName",
    },
    "MiddleName": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "MiddleName",
    },
    "lblLastName": {
        "type": "StaticText",
        "label": "Last Name:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLastName",
    },
    "LastName": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "LastName",
    },
    "lblStatus": {
        "type": "StaticText",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblStatus",
    },
    "Status": {
        "type": "ComboBox",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Status",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Status';",
        "choicevalue": 0,
    },
    "lblBaptized": {
        "type": "StaticText",
        "label": "Baptized:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblBaptized",
    },
    "Baptized": {
        "type": "CheckBox",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Baptized",
    },
    "lblConfirmed": {
        "type": "StaticText",
        "label": "Confirmed:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblConfirmed",
    },
    "Confirmed": {
        "type": "CheckBox",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Confirmed",
    },
    "lblMember": {
        "type": "StaticText",
        "label": "Member:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblMember",
    },
    "Member": {
        "type": "CheckBox",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Member",
    },
    "lblAssociateMember": {
        "type": "StaticText",
        "label": "Associate Member:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAssociateMember",
    },
    "AssociateMember": {
        "type": "CheckBox",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "AssociateMember",
    },
    #        "lblPicture" : {
    #        "Picture" : {
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "name": "Note",
        "style": wx.TE_MULTILINE,
    },
}
#
#   Person Address Table
#
frmPersonAddressCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmPersonAddressCONST["FormHeight"], frmPersonAddressCONST["Fieldheight"])

frmPersonAddressFORM = {
    "type": "Frame",
    "title": "frmPersonAddress : Person Address Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmPersonAddressCONST["FormWidth"], frmPersonAddressCONST["FormHeight"]),
    "name": "frmPersonAddress",
    "tablename": "tblPersonAddress",
    "SQL": "SELECT * FROM tblPersonAddress;",
    "style": wx.CAPTION,
}
frmPersonAddressCONTROLS = {
    "lblPerson": {
        "type": "StaticText",
        "label": "Person:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPerson",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson;",
        "choicevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson WHERE ID= {value};",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "lblLabel": {
        "type": "StaticText",
        "label": "Label:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLabel",
    },
    "AddressLabel": {
        "type": "ComboBox",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "AddressLabel",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'AddressLabel';",
        "choicevalue": 0,
    },
    "lblAddress": {
        "type": "StaticText",
        "label": "Address:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAddress:",
    },
    "Address": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "Address",
    },
    "Address2": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.nextline()),
        "size": wx.Size(300, 30),
        "name": "Address2",
    },
    "lblCity": {
        "type": "StaticText",
        "label": "City:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "City": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "City",
    },
    "lblState": {
        "type": "StaticText",
        "label": "City:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "State": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "State",
    },
    "lblZip": {
        "type": "StaticText",
        "label": "Zip:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblZip:",
    },
    "Zip": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valLen5,
        "name": "Zip",
    },
    "lblStartDate": {
        "type": "StaticText",
        "label": "Start Date:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblStartDate",
    },
    "StartDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "StartDate",
    },
    "lblEndDate": {
        "type": "StaticText",
        "label": "End Date:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblEndDate",
    },
    "EndDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "EndDate",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}
#
#   Person Contact Table
#
frmPersonContactCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmPersonContactCONST["FormHeight"], frmPersonContactCONST["Fieldheight"])

frmPersonContactFORM = {
    "type": "Frame",
    "title": "frmPersonContact : Person Address Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmPersonContactCONST["FormWidth"], frmPersonContactCONST["FormHeight"]),
    "name": "frmPersonContact",
    "tablename": "tblPersonContact",
    "SQL": "SELECT * FROM tblPersonContact;",
    "style": wx.CAPTION,
}
frmPersonContactCONTROLS = {
    "lblPerson": {
        "type": "StaticText",
        "label": "Person:",
        "pos": wx.Point(frmPersonContactCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPerson",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson;",
        "choicevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson WHERE ID={value};",
        "pos": wx.Point(frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "lblLabel": {
        "type": "StaticText",
        "label": "Label:",
        "pos": wx.Point(frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLabel",
    },
    "ContactLabel": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "ContactLabel",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ContactLabel';",
        "choicevalue": 0,
    },
    "lblType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": wx.Point(frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblType",
    },
    "ContactType": {
        "type": "ComboBox",
        "pos": wx.Point(frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "type",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ContactType';",
        "choicevalue": 0,
    },
    "lblContact": {
        "type": "StaticText",
        "label": "Contact:",
        "pos": wx.Point(frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblContact",
    },
    "Contact": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Contact",
    },
    "lblUnlisted": {
        "type": "StaticText",
        "label": "Unlisted:",
        "pos": wx.Point(frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblUnlisted",
    },
    "Unlisted": {
        "type": "CheckBox",
        "pos": wx.Point(frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Unlisted",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}
#
#   Person Date Table
#
frmPersonDateCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmPersonDateCONST["FormHeight"], frmPersonDateCONST["Fieldheight"])

frmPersonDateFORM = {
    "type": "Frame",
    "title": "frmPersonDate : Person Address Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmPersonDateCONST["FormWidth"], frmPersonDateCONST["FormHeight"]),
    "name": "frmPersonDate",
    "tablename": "tblPersonDate",
    "SQL": "SELECT * FROM tblPersonDate;",
    "style": wx.CAPTION,
}
frmPersonDateCONTROLS = {
    "lblPerson": {
        "type": "StaticText",
        "label": "Person:",
        "pos": wx.Point(frmPersonDateCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPerson",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson;",
        "choicevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson WHERE ID = {value};",
        "pos": wx.Point(frmPersonDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "lblType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": wx.Point(frmPersonDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblType",
    },
    "DateType": {
        "type": "ComboBox",
        "pos": wx.Point(frmPersonDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "DateType",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'DateType';",
        "choicevalue": 0,
    },
    "lblDate": {
        "type": "StaticText",
        "label": "Date:",
        "pos": wx.Point(frmPersonDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDate",
    },
    "Date": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        # 'style':
        "validator": valDateAndNull,
        "name": "Date",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmPersonDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmPersonDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}

#
#   Person Date Grid Form
#
frmPersonDateGridCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmPersonDateGridCONST["FormHeight"], frmPersonDateGridCONST["Fieldheight"])

frmPersonDateGridFORM = {
    "type": "Frame",
    "title": "frmPersonDate : Person Address Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmPersonDateCONST["FormWidth"], frmPersonDateCONST["FormHeight"]),
    "name": "frmPersonDate",
    "tablename": "tblPersonDate",
    "SQL": "SELECT * FROM tblPersonDate ORDER BY PersonID;",
    "style": wx.CAPTION,
}
frmPersonDateGridCONTROLS = {
    "lblPerson": {
        "type": "StaticText",
        "label": "Person:",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPerson",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson;",
        "choicevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson WHERE ID = {value};",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "dvlPersonDate": {
        "type": "DataViewListCtrl",
        "column": [("type", 100), ("Date", 150), ("Note", 200)],
        "columnSQL": "SELECT DateType,Date,Note FROM tblPersonDate WHERE PersonID = {value};",
        "value": "PersonID",
        "pos": wx.Point(frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "size": wx.Size(600, 300),
    },
}

#
#   Family Table
#
frmFamilyCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 325 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmFamilyCONST["FormHeight"], frmFamilyCONST["Fieldheight"])

frmFamilyFORM = {
    "type": "Frame",
    "title": "frmFamily : Family Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmFamilyCONST["FormWidth"], frmFamilyCONST["FormHeight"]),
    "name": "frmFamily",
    "tablename": "tblFamily",
    "SQL": "SELECT ID, ChurchID, FamilyName, MarriageStatus, Directory, Note FROM tblFamily ORDER BY FamilyName;",
    "style": wx.CAPTION,
}
frmFamilyCONTROLS = {
    "lblChurchID": {
        "type": "StaticText",
        "label": "Church:",
        "pos": wx.Point(frmFamilyCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblChurchID",
    },
    "ChurchID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Church FROM tblChurch;",
        "choicevalue": 0,
        "lkpSQL": "SELECT Church FROM tblChurch WHERE ID={value};",
        "pos": wx.Point(frmFamilyCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "ChurchID",
    },
    "lblFamilyName": {
        "type": "StaticText",
        "label": "Family Name:",
        "pos": wx.Point(frmFamilyCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblFamilyName",
    },
    "FamilyName": {
        "type": "TextCtrl",
        "value": "",
        "pos": wx.Point(frmFamilyCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "FamilyName",
    },
    "lblMarriageStatus": {
        "type": "StaticText",
        "label": "Marriage Status:",
        "pos": wx.Point(frmFamilyCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblMarriageStatus",
    },
    "MarriageStatus": {
        "type": "ComboBox",
        "pos": wx.Point(frmFamilyCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "MarriageStatus",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'MarriageStatus';",
        "choicevalue": 0,
    },
    "lblDirectory": {
        "type": "StaticText",
        "label": "Directory?:",
        "pos": wx.Point(frmFamilyCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDirectory",
    },
    "Directory": {
        "type": "CheckBox",
        "pos": wx.Point(frmFamilyCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Directory",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmFamilyCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "name": "Note",
        "style": wx.TE_MULTILINE,
    },
}
#
#   FamilyAddress Table
#
frmFamilyAddressCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmFamilyAddressCONST["FormHeight"], frmFamilyAddressCONST["Fieldheight"])


frmFamilyAddressFORM = {
    "type": "Frame",
    "title": "frmFamilyAddress : FamilyAddress Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmFamilyAddressCONST["FormWidth"], frmFamilyAddressCONST["FormHeight"]),
    "name": "frmFamilyAddress",
    "tablename": "tblFamilyAddress",
    "SQL": "SELECT * FROM tblFamilyAddress;",
    "style": wx.CAPTION,
}
frmFamilyAddressCONTROLS = {
    "lblFamilyID": {
        "type": "StaticText",
        "label": "Family:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblFamilyID",
    },
    "FamilyID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, FamilyName FROM tblFamily;",
        "choicevalue": 0,
        "lkpSQL": "SELECT FamilyName FROM tblFamily WHERE ID={value};",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "FamilyID",
    },
    "lblLabel": {
        "type": "StaticText",
        "label": "Label:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLabel",
    },
    "AddressLabel": {
        "type": "ComboBox",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "AddressLabel",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'AddressLabel';",
        "choicevalue": 0,
    },
    "lblAddress": {
        "type": "StaticText",
        "label": "Address:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAddress:",
    },
    "Address": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "Address",
    },
    "Address2": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.nextline()),
        "size": wx.Size(300, 30),
        "name": "Address2",
    },
    "lblCity": {
        "type": "StaticText",
        "label": "City:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "City": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "City",
    },
    "lblState": {
        "type": "StaticText",
        "label": "City:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "State": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valNotNUll,
        "name": "State",
    },
    "lblZip": {
        "type": "StaticText",
        "label": "Zip:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblZip:",
    },
    "Zip": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valLen5,
        "name": "Zip",
    },
    "lblStartDate": {
        "type": "StaticText",
        "label": "Start Date:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblStartDate",
    },
    "StartDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "StartDate",
    },
    "lblEndDate": {
        "type": "StaticText",
        "label": "End Date:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblEndDate",
    },
    "EndDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "EndDate",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}
#
#   FamilyContact Table
#
frmFamilyContactCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmFamilyContactCONST["FormHeight"], frmFamilyContactCONST["Fieldheight"])


frmFamilyContactFORM = {
    "type": "Frame",
    "title": "frmFamilyContact : Person Address Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmFamilyContactCONST["FormWidth"], frmFamilyContactCONST["FormHeight"]),
    "name": "frmFamilyContact",
    "tablename": "tblFamilyContact",
    "SQL": "SELECT * FROM tblFamilyContact;",
    "style": wx.CAPTION,
}
frmFamilyContactCONTROLS = {
    "lblFamilyID": {
        "type": "StaticText",
        "label": "Family:",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblFamilyID",
    },
    "FamilyID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, FamilyName FROM tblFamily;",
        "choicevalue": 0,
        "lkpSQL": "SELECT FamilyName FROM tblFamily WHERE ID={value};",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "FamilyID",
    },
    "lblLabel": {
        "type": "StaticText",
        "label": "Label:",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLabel",
    },
    "ContactLabel": {
        "type": "ComboBox",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Label",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ContactLabel';",
        "choicevalue": 0,
    },
    "lblType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblType",
    },
    "ContactType": {
        "type": "ComboBox",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "type",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ContactType';",
        "choicevalue": 0,
    },
    "lblContact": {
        "type": "StaticText",
        "label": "Contact:",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblContact",
    },
    "Contact": {
        "type": "StaticText",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Contact",
    },
    "lblUnlisted": {
        "type": "StaticText",
        "label": "Unlisted:",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblUnlisted",
    },
    "Unlisted": {
        "type": "CheckBox",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Unlisted",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "value": "",
        "pos": wx.Point(frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}
#
#   Family Date Table
#
frmFamilyDateCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmFamilyDateCONST["FormHeight"], frmFamilyDateCONST["Fieldheight"])
frmFamilyDateFORM = {
    "type": "Frame",
    "title": "frmFamilyDate : Person Address Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmFamilyDateCONST["FormWidth"], frmFamilyDateCONST["FormHeight"]),
    "name": "frmFamilyDate",
    "tablename": "tblFamilyDate",
    "SQL": "SELECT * FROM tblFamilyDate;",
    "style": wx.CAPTION,
}
frmFamilyDateCONTROLS = {
    "lblFamilyID": {
        "type": "StaticText",
        "label": "Family:",
        "pos": wx.Point(frmFamilyDateCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblFamilyID",
    },
    "FamilyID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, FamilyName FROM tblFamily;",
        "choicevalue": 0,
        "lkpSQL": "SELECT FamilyName FROM tblFamily WHERE ID={value};",
        "pos": wx.Point(frmFamilyDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "FamilyID",
    },
    "lblType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": wx.Point(frmFamilyDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblType",
    },
    "DateType": {
        "type": "ComboBox",
        "pos": wx.Point(frmFamilyDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "DateType",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'DateType';",
        "choicevalue": 0,
    },
    "lblDate": {
        "type": "StaticText",
        "label": "Date:",
        "pos": wx.Point(frmFamilyDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDate",
    },
    "Date": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "Date",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmFamilyDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmFamilyDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}

#
#   tblSkill - Add/Edit/Delete Skill
#
frmSkillCONST = {
    "FormWidth": 620,
    "FormHeight": 300,
    "ButtonRow": 300 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmSkillCONST["FormHeight"], frmSkillCONST["Fieldheight"])
frmSkillFORM = {
    "type": "Frame",
    "title": "frmSkill : Skill Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmSkillCONST["FormWidth"], frmSkillCONST["FormHeight"]),
    "name": "frmSkill",
    "tablename": "tblSkill",
    "SQL": "SELECT * FROM tblSkill;",
    "style": wx.CAPTION,
}
frmSkillCONTROLS = {
    "lblSkill": {
        "type": "StaticText",
        "label": "Skill:",
        "pos": wx.Point(frmSkillCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lbl***",
    },
    "Skill": {
        "type": "TextCtrl",
        "pos": wx.Point(frmSkillCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Skill",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmSkillCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmSkillCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        # 'validator': ,
        "name": "Note",
    },
}
#
#   tblProject - Add/Edit//Delete Project
#
frmProjectCONST = {
    "FormWidth": 620,
    "FormHeight": 600,
    "ButtonRow": 600 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmProjectCONST["FormHeight"], frmProjectCONST["Fieldheight"])
frmProjectFORM = {
    "type": "Frame",
    "title": "frmProject : Project Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmProjectCONST["FormWidth"], frmProjectCONST["FormHeight"]),
    "name": "frmProject",
    "tablename": "tblProject",
    "SQL": "SELECT * FROM tblProject;",
    "style": wx.CAPTION,
}
frmProjectCONTROLS = {
    "lblChurchID": {
        "type": "StaticText",
        "label": "Church:",
        "pos": wx.Point(frmProjectCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblChurchID",
    },
    "ChurchID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Church FROM tblChurch;",
        "choicevalue": 0,
        "lkpSQL": "SELECT Church FROM tblChurch WHERE ID={value};",
        "pos": wx.Point(frmProjectCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "ChurchID",
    },
    "lblDescription": {
        "type": "StaticText",
        "label": "Description:",
        "pos": wx.Point(frmProjectCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDescription",
    },
    "Description": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Description",
    },
    #    "lblProjectDate": {
    #        "type": "StaticText",
    #        "label": "Project Date:",
    #        "pos": wx.Point(frmProjectCONST["FormColumn1"], FormLineNumber.nextline()),
    #        "name": "lblProjectDate",
    #    },
    #    "ProjectDate": {
    #        "type": "TextCtrl",
    #        "pos": wx.Point(frmProjectCONST["FormColumn2"], FormLineNumber.sameline()),
    #        "size": wx.Size(300, 30),
    #        "validator": valDateAndNull,
    #        "name": "ProjectDate",
    #    },
    "lblBegun": {
        "type": "StaticText",
        "label": "Begun:",
        "pos": wx.Point(frmProjectCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblBegun",
    },
    "Begun": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "Begun",
    },
    "lblComplete": {
        "type": "StaticText",
        "label": "Complete:",
        "pos": wx.Point(frmProjectCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblComplete",
    },
    "Complete": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "Complete",
    },
    "lblAgeLimit": {
        "type": "StaticText",
        "label": "Age Limit:",
        "pos": wx.Point(frmProjectCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAgeLimit",
    },
    "AgeLimit": {
        "type": "ComboBox",
        "pos": wx.Point(frmProjectCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "validator": valOnlyNone,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'AgeLimit';",
        "choicevalue": 0,
        "name": "AgeLimit",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmProjectCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
    },
}

#
#   tblProjectTask - Add/Edit//Delete ProjectTask
#
frmProjectTaskCONST = {
    "FormWidth": 620,
    "FormHeight": 600,
    "FormButtonRow": 600 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmProjectTaskCONST["FormHeight"], frmProjectTaskCONST["Fieldheight"])

frmProjectTaskFORM = {
    "type": "Frame",
    "title": "frmProjectTask : ProjectTask Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmProjectTaskCONST["FormWidth"], frmProjectTaskCONST["FormHeight"]),
    "name": "frmProjectTask",
    "tablename": "tblProjectTask",
    "SQL": "SELECT * FROM tblProjectTask ORDER BY ProjectID, Complete, Sequence;",
    "style": wx.CAPTION,
}
frmProjectTaskCONTROLS = {
    "lblProjectID": {
        "type": "StaticText",
        "label": "ProjectID",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblProjectID",
    },
    "ProjectID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Description FROM tblProject;",
        "choicevalue": 0,
        "lkpSQL": "SELECT Description FROM tblProject WHERE ID={value};",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "ProjectID",
    },
    "lblComplete": {
        "type": "StaticText",
        "label": "Complete:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblComplete",
    },
    "Complete": {
        "type": "CheckBox",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "Complete",
    },
    "lblSequence": {
        "type": "StaticText",
        "label": "Sequence:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSquence",
    },
    "Sequence": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Sequence",
    },
    "lblDescription": {
        "type": "StaticText",
        "label": "Description:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDescription",
    },
    "Description": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Description",
    },
    "lblStartDate": {
        "type": "StaticText",
        "label": "Start Date:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblStartDate",
    },
    "StartDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateAndNull,
        "name": "StartDate",
    },
    "lblEndDate": {
        "type": "StaticText",
        "label": "End Date:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblEndDate",
    },
    "EndDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "EndDate",
        "validator": valDateAndNull,
    },
    "lblDueDate": {
        "type": "StaticText",
        "label": "Due Date:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDueDate",
    },
    "DueDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "DueDate",
        "validator": valDateAndNull,
    },
    "lblAssignedTo": {
        "type": "StaticText",
        "label": "Assigned To:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAssignedTo",
    },
    "AssignedTo": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "AssignedTo",
    },
    # Documents
    # Dependanceies
    "lblEstimate": {
        "type": "StaticText",
        "label": "Estimate:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblEstimate",
    },
    "Estimate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Estimate",
    },
    "lblEstimateType": {
        "type": "StaticText",
        "label": "Estimate Type:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblEstimateType",
    },
    "EstimateType": {
        "type": "ComboBox",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "EstimateType",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'EstimateType';",
        "choicevalue": 0,
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectTaskCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
    },
}
#
#   tblProjectSkill - Add/Edit/Delete Project Skill
#
frmProjectSkillCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmProjectSkillCONST["FormHeight"], frmProjectSkillCONST["Fieldheight"])

frmProjectSkillFORM = {
    "type": "Frame",
    "title": "frmProjectSkill : ProjectSkill Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmProjectSkillCONST["FormWidth"], frmProjectSkillCONST["FormHeight"]),
    "name": "frmProjectSkill",
    "tablename": "tblProjectSkill",
    "SQL": "SELECT * FROM tblProjectSkill ORDER BY ProjectID;",
    "style": wx.CAPTION,
}
frmProjectSkillCONTROLS = {
    "lblProjectID": {
        "type": "StaticText",
        "label": "ProjectID",
        "pos": wx.Point(frmProjectSkillCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblProjectID",
    },
    "ProjectID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Description FROM tblProject;",
        "choicevalue": 0,
        "lkpSQL": "SELECT Description FROM tblProject WHERE ID={value};",
        "pos": wx.Point(frmProjectSkillCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "ProjectID",
    },
    "lblSkillID": {
        "type": "StaticText",
        "label": "Skill:",
        "pos": wx.Point(frmProjectSkillCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSkillID",
    },
    "Skill": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Skill FROM tblSkill;",
        "choicevalue": 0,
        "lkpSQL": "SELECT Skill FROM tblSkill WHERE ID={value};",
        "pos": wx.Point(frmProjectSkillCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "Skill",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmProjectSkillCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmProjectSkillCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
    },
}
#
#   Attendance Add/Edit/Delete
#
frmAttendanceCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 750 - 75,
    "FormColumn1": 0,
    "FormColumn2": 145,
    "FormColumn3": 500,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmAttendanceCONST["FormHeight"], frmAttendanceCONST["Fieldheight"])

frmAttendanceFORM = {
    "type": "Frame",
    "title": "frmAttendance : Service Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmAttendanceCONST["FormWidth"], frmAttendanceCONST["FormHeight"]),
    "name": "frmAttendance",
    "tablename": "tblAttendance",
    "SQL": "SELECT * FROM tblAttendance ORDER BY DateTime DESC;",
    "style": wx.CAPTION,
}
frmAttendanceCONTROLS = {
    "lblPersonID": {
        "type": "StaticText",
        "label": "Person ID :",
        "pos": wx.Point(frmAttendanceCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPersonID",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) FROM tblPerson;",
        "choicevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) FROM tblPerson WHERE ID={value};",
        "pos": wx.Point(frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "lblAttendanceEventID": {
        "type": "StaticText",
        "label": "Attenandance Event ID:",
        "pos": wx.Point(frmAttendanceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAttendanceEventID",
    },
    "AttendanceEventID": {
        "type": "TextCtrl",
        "pos": wx.Point(frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "AttendanceID",
    },
    "lblDateTime": {
        "type": "StaticText",
        "label": "Attendance Date: ",
        "pos": wx.Point(frmAttendanceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDateTime",
    },
    "DateTime": {
        "type": "TextCtrl",
        "pos": wx.Point(frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "DateTime",
        "validator": valDateandTime,
    },
    "lblAttendanceTypeID": {
        "type": "StaticText",
        "label": "Attendance Type ID:",
        "pos": wx.Point(frmAttendanceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAttendanceTypeID",
    },
    "AttendanceTypeID": {
        "type": "TextCtrl",
        "pos": wx.Point(frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "lblAttendanceTypeID",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmAttendanceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        # 'validator': ,
        "name": "Note",
    },
}

#
#   Choices Lists
#
frmChoicesCONST = {
    "FormWidth": 620,
    "FormHeight": 550,
    "FormButtonRow": 550 - 75,
    "FormColumn1": 0,
    "FormColumn2": 100,
    "FormColumn3": 155,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmChoicesCONST["FormHeight"], frmChoicesCONST["Fieldheight"])
frmChoicesFORM = {
    "type": "Frame",
    "title": "frmChoices : Choices Edit Form",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmChoicesCONST["FormWidth"], frmChoicesCONST["FormHeight"]),
    "name": "frmChoices",
    "tablename": "tblChoices",
    "SQL": "SELECT * FROM tblChoices;",
    "style": wx.CAPTION,
}
frmChoicesCONTROLS = {
    "lblField": {
        "type": "StaticText",
        "label": "Field:",
        "pos": wx.Point(frmChoicesCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblField",
    },
    "Field": {
        "type": "TextCtrl",
        "pos": wx.Point(frmChoicesCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "Field",
    },
    "lblChoices": {
        "type": "StaticText",
        "label": "Choices:",
        "pos": wx.Point(frmChoicesCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblChoices",
    },
    "Choices": {
        "type": "TextCtrl",
        "list": True,
        "pos": wx.Point(frmChoicesCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 300),
        "style": TE_MULTILINE,
        "name": "Choices",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmChoicesCONST["FormColumn1"], FormLineNumber.nextline(270)),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmChoicesCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
    },
}

#
#   Propers Display Form
#

frmPropersDisplayCONST = {
    "FormWidth": 550,
    "FormHeight": 800,
    "FormButtonRow": 800 - 75,
    "FormColumn1": 30,
    "FormColumn2": 150,
    "FormColumn3": 425,
    "Fieldheight": 30,
}
FormLineNumber = pos(30, frmPropersDisplayCONST["FormHeight"], frmPropersDisplayCONST["Fieldheight"])
frmPropersDisplayFORM = {
    "type": "Frame",
    "subformtype": "StaticBox",
    "label": "Propers",
    "title": "frmPropersDisplay : PropersDisplay",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmPropersDisplayCONST["FormWidth"], frmPropersDisplayCONST["FormHeight"]),
    "name": "frmPropersDisplay",
    "tablename": "tblPropers",
    "SQL": "SELECT Lectionary,Sort,Series,Season,LiturgicalDate,CalendarDateFrom,CalendarDateTo,Color FROM tblPropers;",
    "style": wx.CAPTION,
}
frmPropersDisplayCONTROLS = {
    "lblLectionary": {
        "type": "StaticText",
        "label": "Lectionary:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblLectionary",
    },
    "Lectionary": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Lectionary",
        "label": "Lectionary",
        "readonly": True,
    },
    "lblSeries": {
        "type": "StaticText",
        "label": "Series:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSeires",
    },
    "Series": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Series",
        "readonly": True,
    },
    "lblSeason": {
        "type": "StaticText",
        "label": "Season:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSeason",
    },
    "Season": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Season",
        "readonly": True,
    },
    "lblLiturgicalDate": {
        "type": "StaticText",
        "label": "Liturgical Date:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLiturgicalDate",
    },
    "LiturgicalDate": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "LiturgicalDate",
        "readonly": True,
    },
    "lblCalendarDateFrom": {
        "type": "StaticText",
        "label": "From:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCalendarDateFrom",
    },
    "CalendarDateFrom": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "CalendarDateFrom",
        "readonly": True,
    },
    "lblCalendarDateTo": {
        "type": "StaticText",
        "label": "To:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCalendarDateTo",
    },
    "CalendarDateTo": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "CalendarDateTo",
        "readonly": True,
    },
    "lblColor": {
        "type": "StaticText",
        "label": "Liturgical Color:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblColor",
    },
    "Color": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Color",
        "readonly": True,
    },
    "lblIntroit": {
        "type": "StaticText",
        "label": "Introit:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblIntroit",
    },
    "Introit": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Introit",
        "readonly": True,
    },
    "lblTheme": {
        "type": "StaticText",
        "label": "Theme:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline(75)),
        "name": "lblTheme",
    },
    "Theme": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Theme",
        "readonly": True,
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn1"], FormLineNumber.nextline(75)),
        "name": "lblNote",
    },
    "Note": {
        "type": "StaticText",
        "pos": wx.Point(frmPropersDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
        "readonly": True,
    },
}

#
#   Readings Display Form
#
frmReadingListCONST = {
    "FormWidth": 800,
    "FormHeight": 350,
    "FormButtonRow": 350 - 75,
    "FormColumn1": 30,
    "FormColumn2": 150,
    "FormColumn3": 425,
    "Fieldheight": 30,
}
FormLineNumber = pos(30, frmReadingListCONST["FormHeight"], frmReadingListCONST["Fieldheight"])
frmReadingListFORM = {
    "type": "Frame",
    "title": "frmReadingList : ReadingsDisplay",
    "subformtype": "StaticBox",
    "label": "Readings",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmReadingListCONST["FormWidth"], frmReadingListCONST["FormHeight"]),
    "name": "frmReadingList",
    "tablename": "tblPropers",
    #"SQL": "SELECT ID /*tb:dvlReadings*/ FROM tblPropers WHERE ID={ID};",
    "style": wx.CAPTION,
}
frmReadingListCONTROLS = {
    "dvlReadings": {
        "type": "DataViewListCtrl",
        "column": [("Reading", 100), ("ReadingReference", 300), ("Note", 100)],
        "columnSQL": "SELECT Reading, ReadingReference, Note FROM tblReading WHERE PropersID = {value};",
        "value": "ID",
        "pos": wx.Point(25, 30),
        "size": wx.Size(frmReadingListCONST["FormWidth"] - 40, frmReadingListCONST["FormHeight"] - 100),
    },
}
#
#   Alternate Readings Display Form
#
frmAltReadingsDisplayCONST = {
    "FormWidth": 800,
    "FormHeight": 350,
    "FormButtonRow": 350 - 75,
    "FormColumn1": 30,
    "FormColumn2": 150,
    "FormColumn3": 425,
    "Fieldheight": 30,
}
FormLineNumber = pos(30, frmAltReadingsDisplayCONST["FormHeight"], frmAltReadingsDisplayCONST["Fieldheight"])
frmAltReadingsDisplayFORM = {
    "type": "Frame",
    "title": "frmAltReadingsDisplay : Alt Readings Display",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmAltReadingsDisplayCONST["FormWidth"], frmAltReadingsDisplayCONST["FormHeight"]),
    "name": "frmAltReadingsDisplay",
    "tablename": "tblReading",
    "SQL": "SELECT * FROM tblReading;",
    "style": wx.CAPTION,
}
frmAltReadingsDisplayCONTROLS = {
    "boxReading": {
        "type": "StaticBox",
        "label": "Alternate Readings",
        "pos": wx.Point(10, 10),
        "size": wx.Size(frmAltReadingsDisplayCONST["FormWidth"] - 20, frmAltReadingsDisplayCONST["FormHeight"] - 50),
    },
    "dvlAltReadings": {
        "type": "DataViewListCtrl",
        "column": [("Reading", 100), ("ReadingReference", 300), ("Note", 100)],
        "columnSQL": "SELECT Reading, ReadingReference, Note FROM tblAltReading WHERE ServiceID = {value};",
        "value": "ID",
        "pos": wx.Point(25, 30),
        "size": wx.Size(frmAltReadingsDisplayCONST["FormWidth"] - 40, frmAltReadingsDisplayCONST["FormHeight"] - 100),
    },
}

#
#   Hymn Usage Display
#
frmHymnUsageDisplayCONST = {
    "FormWidth": 800,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 30,
    "FormColumn2": 150,
    "FormColumn3": 425,
    "Fieldheight": 30,
}
FormLineNumber = pos(30, frmHymnUsageDisplayCONST["FormHeight"], frmHymnUsageDisplayCONST["Fieldheight"])
frmHymnUsageDisplayFORM = {
    "type": "Frame",
    "title": "frmHymnUsageDisplay : HymnUsageDisplay",
    "pos": wx.Point(10, 10),
    "size": wx.Size(frmHymnUsageDisplayCONST["FormWidth"], frmHymnUsageDisplayCONST["FormHeight"]),
    "name": "frmHymnUsageDisplay",
    "tablename": "tblService",
    "SQL": "SELECT ID, DateTime /*tb:dvlHymnUsage */ FROM tblService;",
    "style": wx.CAPTION,
    "linkedform": {
        "frmHymnSearch": {
            "pos": wx.Point(100, 100),
            "bindbtn": "btnHymnAdd",
            "controls": ["Close"],
            "style": (wx.CAPTION), #| wx.STAY_ON_TOP),
        },
        "frmHymnUsage": {
            "SQL": "SELECT * FROM tblHymnUsage WHERE ID = {ID};",
            "bindbtn": "btnHymnUpdate",
            "controls": ["Close", "Navigation"]},
    },
}
frmHymnUsageDisplayCONTROLS = {
    "lblService": {
        "type": "StaticText",
        "label": "Service:",
        "pos": wx.Point(frmHymnUsageDisplayCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblService",
    },
    "DateTime": {
        "type": "TextCtrl",
        "pos": wx.Point(frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateandTime,
        "name": "DateTime",
        "readonly": True,
    },
    "boxHymns": {
        "type": "StaticBox",
        "label": "Hymns",
        "pos": wx.Point(10, FormLineNumber.nextline()),
        "size": wx.Size(frmHymnUsageDisplayCONST["FormWidth"] - 20, frmHymnUsageDisplayCONST["FormButtonRow"] - 75),
    },
    "dvlHymnUsage": {
        "type": "DataViewListCtrl",
        "column": [("ID",1), ("UsedAs", 100), ("Hymn", 75), ("Title", 300), ("Note", 200)],
        "columnSQL": "SELECT ID, UsedAs, concat(HymnalPrefix,Hymn) as Hymn, Title, Note FROM vwHymnUsage WHERE ServiceID = {value};",
        "value": "ID",
        "pos": wx.Point(25, FormLineNumber.nextline()),
        "size": wx.Size(frmHymnUsageDisplayCONST["FormWidth"] - 40, frmHymnUsageDisplayCONST["FormButtonRow"] - 165),
        "name" : "dvlHymnUsage",
    },
    "btnHymnAdd": {
        "type": "Button",
        "label": "Add",
        "pos": wx.Point(20, frmHymnUsageDisplayCONST["FormButtonRow"] - 60),
        "name": "btnHymnAdd",
    },
    "btnHymnUpdate" : {
        "type": "Button",
        "label": "Update",
        "pos": wx.Point(110, frmHymnUsageDisplayCONST["FormButtonRow"] - 60),
        "name" : "btnHymnUpdate",
    },
    "btnHymnDelete": {
        "type":"Button",
        "label": "Delete",
        "pos": wx.Point(200, frmHymnUsageDisplayCONST["FormButtonRow"] - 60),
        "name" : "btnHymnDelete",
    },
    "btnUpdateService": {
        "type":"Button",
        "label": "Update Service",
        "pos":wx.Point(10, frmHymnUsageDisplayCONST["FormButtonRow"]),
        "name" : "btnUpdateService",
    }
}


#
#   Service Add/Edit/Delete
#
frmServiceCONST = {
    "FormWidth": 1300,
    "FormHeight": 900,
    "FormButtonRow": 900 - 75,
    "FormColumn1": 0,
    "FormColumn2": 145,
    "FormColumn3": 475,
    "FormColumn4": 1175,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmServiceCONST["FormHeight"], frmServiceCONST["Fieldheight"])
frmServiceFORM = {
    "type": "Frame",
    "title": "frmService : Service Edit Form",
    "pos": wx.Point(20, 20),
    "size": wx.Size(frmServiceCONST["FormWidth"], frmServiceCONST["FormHeight"]),
    "name": "frmService",
    "tablename": "tblService",
    "SQL": "SELECT * FROM tblService ORDER BY DateTime DESC;",
    "style": wx.CAPTION,
    "linkedform": {
        "frmHymnUsageDisplay": {
            "pos": wx.Point(frmServiceCONST["FormWidth"] - 350, 100),
            "SQL": "SELECT ID, DateTime /*tb:dvlHymnUsage*/ FROM tblService WHERE ID = {ID};",
            "controls": ["Close"],
            "bindbtn": "btnHymns",
            "style": (wx.CAPTION), # | wx.STAY_ON_TOP),
        },
        "frmAltReadingsDisplay": {
            "pos": wx.Point(frmServiceCONST["FormColumn3"] + 300, frmPropersCONST["FormHeight"] + 100),
            "SQL": "SELECT * FROM tblService WHERE ID = {ID};",
            "controls": ["Close"],
            "bindbtn": "btnAtlReadings",
            "style": (wx.CAPTION), # | wx.STAY_ON_TOP),
        },
    },
    "subform": {
        "frmPropers": {
            "type": "StaticBox",
            "label": "Propers",
            "pos": wx.Point(frmServiceCONST["FormColumn3"], 10),
            "SQL": "SELECT Lectionary,Sort,Series,Season,LiturgicalDate,CalendarDateFrom,CalendarDateTo,Color FROM tblPropers WHERE ID = {PropersID};",
            "controls": [],
            "readonly": True,
        },
        "frmReadingList": {
            "type": "StaticBox",
            "label": "Readings",
            "SQL": "SELECT ID /*tb:dvlReadings*/ FROM tblPropers WHERE ID={ID};",
            "pos": wx.Point(frmServiceCONST["FormColumn3"], frmPropersCONST["FormHeight"] + 10),
            "controls": [],
            "readonly": True,
            "style": wx.STAY_ON_TOP,
        },
    },
}
frmServiceCONTROLS = {
    "lblLectionary": {
        "type": "StaticText",
        "label": "Lectionary:",
        "pos": wx.Point(5, FormLineNumber.sameline()),
        "name": "lblLectionary",
    },
    "lblYear": {
        "type": "StaticText",
        "label": "Year",
        "pos": wx.Point(100, FormLineNumber.sameline()),
        "name": "lblYear",
    },
    "lblToday": {
        "type": "StaticText",
        "label": "Today's Date",
        "pos": wx.Point(145, FormLineNumber.sameline()),
        "name": "lblToday",
    },
    "Lectionary": {
        "type": "StaticText",
        "fcolor": FORMColors["Notice"]["fcolor"],
        "bcolor": FORMColors["Notice"]["bcolor"],
        "pos": wx.Point(15, FormLineNumber.nextline() - 10),
        "lkpSQL": "SELECT ConfigValue FROM tblConfig WHERE ConfigType = 'Lectionary';",
        "Name": "Lectionary",
    },
    "LectionarySeriesYear": {
        "type": "StaticText",
        "fcolor": "BLUE",
        "pos": wx.Point(100, FormLineNumber.sameline() - 10),
        "lkpSQL": "SELECT ConfigValue FROM tblConfig WHERE ConfigType = 'LectionarySeriesYear';",
        "Name": "LectionarySeriesYear",
    },
    "Today": {
        "type": "StaticText",
        "fcolor": "BLUE",
        "date": "today",
        "pos": wx.Point(145, FormLineNumber.sameline() - 10),
        "Name": "lblToday",
    },
    "btnHymns": {
        "type": "Button",
        "label": "Hymns",
        "pos": wx.Point(frmServiceCONST["FormColumn4"], FormLineNumber.sameline()),
        "size": wx.Size(100, 30),
        "name": "btnNew",
    },
    "lblChurchID": {
        "type": "StaticText",
        "label": "Church :",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblChurchID",
    },
    "ChurchID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Church FROM tblChurch;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT Church FROM tblChurch WHERE ID={value};",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "ChurchID",
    },
    "lblDateTime": {
        "type": "StaticText",
        "label": "Service Date/Time:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblServiceDateTime",
    },
    "DateTime": {
        "type": "TextCtrl",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "validator": valDateandTime,
        "name": "DateTime",
    },
    "lblPropersID": {
        "type": "StaticText",
        "label": "Propers:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblPropersID",
    },
    "PropersID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(Series,' ',Season,' ',LiturgicalDate) FROM tblPropers ORDER BY Sort;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT CONCAT(Series,' ',Season,' ',LiturgicalDate) FROM tblPropers  WHERE ID={value} ORDER BY Sort;",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "style": wx.CB_READONLY,
        "name": "PropersID",
    },
    "lblLiturgicalDate": {
        "type": "StaticText",
        "label": "Liturgical Date:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLiturgicalDate",
    },
    "LiturgicalDate": {
        "type": "TextCtrl",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "LiturgicalDate",
    },
    "lblHolyCommunion": {
        "type": "StaticText",
        "label": "Holy Communion:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblHolyCommunion",
    },
    "HolyCommunion": {
        "type": "CheckBox",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "HolyCommunion",
    },
    "lblOrderofServiceID": {
        "type": "StaticText",
        "label": "OrderofService:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblOrderofService",
    },
    "OrderofServiceID": {
        "type": "TextCtrl",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "OrderofServiceID",
    },
    "lblOSNote": {
        "type": "StaticText",
        "label": "OSNote:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblOSNote",
    },
    "OSNote": {
        "type": "TextCtrl",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 130),
        "style": TE_MULTILINE,
        "name": "OSNote",
    },
    "lblPsalmorIntroit": {
        "type": "StaticText",
        "label": "Psalm or Introit:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline(100)),
        "name": "lblPsalmorIntroit",
    },
    "PsalmorIntroit": {
        "type": "ComboBox",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "PsalmorIntroit",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'PsalmorIntroit';",
        "comparevalue": 0,
        "choicevalue": 0,
    },
    "lblSermonText": {
        "type": "StaticText",
        "label": "Sermon:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSermonText",
    },
    "SermonText": {
        "type": "TextCtrl",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "SermonText",
    },
    "lblBulletin": {
        "type": "StaticText",
        "label": "Bulletin:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblBulletin",
    },
    "Bulletin": {
        "type": "TextCtrl",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Bulletin",
    },
    "btnAtlReadings": {
        "type": "Button",
        "label": "Alt Readings",
        "pos": wx.Point(frmServiceCONST["FormColumn4"], FormLineNumber.sameline()),
        "size": wx.Size(100, 30),
        "name": "btnNew",
    },
    "lblInserts": {
        "type": "StaticText",
        "label": "Inserts:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblInserts",
    },
    "Inserts": {
        "type": "TextCtrl",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Inserts",
    },
    "lblCheckListComplete": {
        "type": "StaticText",
        "label": "Check List Complete:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCheckListComplete",
    },
    "CheckListComplete": {
        "type": "CheckBox",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "CheckListComplete",
    },
    "lblCheckListID": {
        "type": "StaticText",
        "label": "Check List ID:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCheckListID",
    },
    "CheckListID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CheckListName FROM tblCheckList;",
        "comparevalue": 0,
        "choicevalue": 1,
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "CheckListID",
    },
    "lblCheckList": {
        "type": "StaticText",
        "label": "CheckList:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCheckList",
    },
    "CheckList": {
        "type": "CheckListBox",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 130),
        "name": "CheckList",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": wx.Point(frmServiceCONST["FormColumn1"], FormLineNumber.nextline(100)),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": wx.Point(frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 100),
        "style": TE_MULTILINE,
        "name": "Note",
    },
}


frmHymnSearchCONST = {
    "FormWidth": 1200,
    "FormHeight": 800,
    "FormButtonRow": 800 - 75,
    "FormColumn1": 10,
    "FormColumn2": 100,
    "FormColumn3": 475,
    "FormColumn4": 1175,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmHymnSearchCONST["FormHeight"], frmHymnSearchCONST["Fieldheight"])
frmHymnSearchFORM = {
    "type": "Frame",
    "title": "frmHymnSearch : Hymn Search Form",
    "pos": wx.Point(20, 20),
    "size": wx.Size(frmHymnSearchCONST["FormWidth"], frmHymnSearchCONST["FormHeight"]),
    "name": "frmHymnSearch",
    "style": wx.CAPTION,
}
frmHymnSearchCONTROLS = {
    "lblSearch": {
        "type": "StaticText",
        "label": "Search:",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblSearch",
    },
    "Search": {
        "type": "TextCtrl",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": wx.Size(300, 30),
        "name": "Search",
        "norecorddata": True,
    },
    "btnByHymn": {
        "type": "Button",
        "label": "By Hymn",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn1"], FormLineNumber.nextline()),
        "size": wx.Size(100, 30),
        "name": "btnByHymn",
    },
    "btnByTitle": {
        "type": "Button",
        "label": "By Title",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn1"] + 100, FormLineNumber.sameline()),
        "size": wx.Size(100, 30),
        "name": "btnByTitle",
    },
    "btnByBible": {
        "type": "Button",
        "label": "By Bible",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn1"] + 200, FormLineNumber.sameline()),
        "size": wx.Size(100, 30),
        "name": "btnByBibile",
    },
    "btnByCategory": {
        "type": "Button",
        "label": "By Category",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn1"] + 300, FormLineNumber.sameline()),
        "size": wx.Size(100, 30),
        "name": "btnByCategroy",
    },
    "btnByNote": {
        "type": "Button",
        "label": "By Note",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn1"] + 400, FormLineNumber.sameline()),
        "size": wx.Size(100, 30),
        "name": "btnByNote",
    },
    "dvlHymnList": {
        "type": "DataViewListCtrl",
        "column": [
            ("ID", 0),
            ("Hymn", 75),
            ("Title", 300),
            ("BibleText", 300),
            ("Category", 200),
            ("Note", 300),
        ],
        "columnSQL": "SELECT ID, CONCAT(HymnalPrefix,Hymn) as Hymn,Title,BibleText,Category,Note FROM vwHymnList ORDER BY Hymn;",
        "value": "*",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn1"], FormLineNumber.nextline()),
        "size": wx.Size(frmHymnSearchCONST["FormWidth"] - 40, frmHymnSearchCONST["FormButtonRow"] - 75),
    },
    "btnAdd": {
        "type": "Button",
        "label": "Add",
        "pos": wx.Point(frmHymnSearchCONST["FormColumn1"], frmHymnSearchCONST["FormButtonRow"]),
        "size": wx.Size(50, 30),
        "name": "btnAdd",
    },
}
