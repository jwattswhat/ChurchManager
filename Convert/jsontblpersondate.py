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
    "pos": (10, 10),
    "size": (frmPersonDateCONST["FormWidth"], frmPersonDateCONST["FormHeight"]),
    "name": "frmPersonDate",
    "tablename": "tblPersonDate",
    "SQL": "SELECT * FROM tblPersonDate;",
    "style": wx.CAPTION,
}
frmPersonDateCONTROLS = {
    "lblPerson": {
        "type": "StaticText",
        "label": "Person:",
        "pos": (frmPersonDateCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPerson",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson;",
        "choicevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson WHERE ID = {value};",
        "pos": (frmPersonDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "lblType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": (frmPersonDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblType",
    },
    "DateType": {
        "type": "ComboBox",
        "pos": (frmPersonDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "DateType",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'DateType';",
        "choicevalue": 0,
    },
    "lblDate": {
        "type": "StaticText",
        "label": "Date:",
        "pos": (frmPersonDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDate",
    },
    "Date": {
        "type": "TextCtrl",
        "pos": (frmPersonDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        # 'style':
        "validator": "valDateAndNull",
        "name": "Date",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmPersonDateCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmPersonDateCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}



pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmPersonDateFORM" : {
        "FORM": frmPersonDateFORM,
        "CONTROLS": frmPersonDateCONTROLS
    }
}

for f in frmPersonDateCONTROLS:
    print (frmPersonDateCONTROLS[f])
    pp.pprint(json.dumps(frmPersonDateCONTROLS[f]))



# pp.pprint(Family)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmPersonDate.json", "w")
f.write(newjson)
f.close()
