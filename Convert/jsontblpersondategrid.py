import pprint
import json
import wx


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

    # incr is an additional amount to add for additional spacing above the line
    def nextline(self, incr=0):
        self.val += self.iter
        self.val += incr
        self._checkoverflow()
        return self.val

    # incr is an additional amount to add for additional spacing above the line
    def sameline(self, incr=0):
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
    "pos": (10, 10),
    "size": (frmPropersCONST["FormWidth"], frmPropersCONST["FormHeight"]),
    "name": "frmPropers",
    "tablename": "tblPropers",
    "SQL": "SELECT Lectionary,Sort,Series,Season,LiturgicalDate,CalendarDateFrom,CalendarDateTo,Color FROM tblPropers ORDER BY Sort;",
    "style": wx.CAPTION,
    "linkedform": {
        "frmReading": {
            "SQL": "SELECT * FROM tblReading WHERE PropersID = {ID};",
            "pos": (frmPropersCONST["FormWidth"] + 20, 10),
            "controls": ["Close", "Navigation"],
            "bindbtn": "btnEditReading",
        }
    },
}
frmPropersCONTROLS = {
    "lblLectionary": {
        "type": "StaticText",
        "label": "Lectionary:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblLectionary",
    },
    "Lectionary": {
        "type": "ComboBox",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Lectionary';",
        "choicevalue": 0,
        "comparevalue": 0,
        "name": "Lectionary",
    },
    "lblSort": {
        "type": "StaticText",
        "label": "Sort:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSort",
    },
    "Sort": {
        "type": "TextCtrl",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Sort",
        # 'validator' : valNumeric, <TODO> Not yet implemented.
    },
    "lblSeries": {
        "type": "StaticText",
        "label": "Series:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSeires",
    },
    "Series": {
        "type": "ComboBox",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Series",
        "savestyle": "wx.CB_READONLY",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Series';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblSeason": {
        "type": "StaticText",
        "label": "Season:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSeason",
    },
    "Season": {
        "type": "ComboBox",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "savestyle": "wx.CB_READONLY",
        "name": "Season",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Season';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblLiturgicalDate": {
        "type": "StaticText",
        "label": "Liturgical Date:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLiturgicalDate",
    },
    "LiturgicalDate": {
        "type": "TextCtrl",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "LiturgicalDate",
        # "validator": valNotNUll,
    },
    "btnEditReading": {
        "type": "Button",
        "label": "Readings",
        "pos": (frmPropersCONST["FormColumn3"], FormLineNumber.sameline()),
        "name": "btnEditReading",
    },
    "lblCalendarDateFrom": {
        "type": "StaticText",
        "label": "From:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCalendarDateFrom",
    },
    "CalendarDateFrom": {
        "type": "TextCtrl",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "CalendarDateFrom",
        #"validator": valDateMMDDAndNull,  # <TODO> This validator isn't being called by wxPython
    },
    "lblCalendarDateTo": {
        "type": "StaticText",
        "label": "To:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCalendarDateTo",
    },
    "CalendarDateTo": {
        "type": "TextCtrl",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "CalendarDateTo",
        #"validator": valDateMMDDAndNull,  # <TODO> This validator isn't being called by wxPython
    },
    "lblColor": {
        "type": "StaticText",
        "label": "Liturgical Color:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblColor",
    },
    "Color": {
        "type": "ComboBox",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Color",
        "savestyle": "wx.CB_READONLY",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Color';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblAltColor": {
        "type": "StaticText",
        "label": "Alt Color:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAltColor",
    },
    "AltColor": {
        "type": "ComboBox",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "AltColor",
        "savestyle": "wx.CB_READONLY",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Color';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmPropersCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmPropersCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "savestyle": "TE_MULTILINE",
        "name": "Note",
    },
}




pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmPersonDateFORM" : {
        "FORM": frmPropersFORM,
        "CONTROLS": frmPropersCONTROLS
    }
}

for f in frmPropersCONTROLS:
    print (frmPropersCONTROLS[f])
    pp.pprint(json.dumps(frmPropersCONTROLS[f]))



# pp.pprint(Family)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmPropers.json", "w")
f.write(newjson)
f.close()
