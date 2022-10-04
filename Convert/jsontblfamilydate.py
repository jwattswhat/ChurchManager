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
    "pos": (10, 10),
    "size": (frmFamilyDateCONST["FormWidth"], frmFamilyDateCONST["FormHeight"]),
    "name": "frmFamilyDate",
    "tablename": "tblFamilyDate",
    "SQL": "SELECT * FROM tblFamilyDate;",
    "style": wx.CAPTION,
}
frmFamilyDateCONTROLS = {
    "lblFamilyID": {
        "type": "StaticText",
        "label": "Family:",
        "pos": (frmFamilyDateCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblFamilyID",
    },
    "FamilyID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, FamilyName FROM tblFamily;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT FamilyName FROM tblFamily WHERE ID={value};",
        "pos": (frmFamilyDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "FamilyID",
    },
    "lblType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": (frmFamilyDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblType",
    },
    "DateType": {
        "type": "ComboBox",
        "pos": (frmFamilyDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "DateType",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'DateType';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblDate": {
        "type": "StaticText",
        "label": "Date:",
        "pos": (frmFamilyDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDate",
    },
    "Date": {
        "type": "TextCtrl",
        "pos": (frmFamilyDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valDateAndNull",
        "name": "Date",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmFamilyDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmFamilyDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}




pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmFamilyDateFORM" : {
        "FORM": frmFamilyDateFORM,
        "CONTROLS": frmFamilyDateCONTROLS
    }
}

for f in frmFamilyDateCONTROLS:
    print (frmFamilyDateCONTROLS[f])
    pp.pprint(json.dumps(frmFamilyDateCONTROLS[f]))



# pp.pprint(Family)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmFamilyDate.json", "w")
f.write(newjson)
f.close()
