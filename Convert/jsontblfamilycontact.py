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
    "title": "frmFamilyContact : Family Address Edit Form",
    "pos": (10, 10),
    "size": (frmFamilyContactCONST["FormWidth"], frmFamilyContactCONST["FormHeight"]),
    "name": "frmFamilyContact",
    "tablename": "tblFamilyContact",
    "SQL": "SELECT * FROM tblFamilyContact;",
    "style": wx.CAPTION,
}
frmFamilyContactCONTROLS = {
    "lblFamilyID": {
        "type": "StaticText",
        "label": "Family:",
        "pos": (frmFamilyContactCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblFamilyID",
    },
    "FamilyID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, FamilyName FROM tblFamily;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT FamilyName FROM tblFamily WHERE ID={value};",
        "pos": (frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "FamilyID",
    },
    "lblLabel": {
        "type": "StaticText",
        "label": "Label:",
        "pos": (frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLabel",
    },
    "ContactLabel": {
        "type": "ComboBox",
        "pos": (frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Label",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ContactLabel';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": (frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblType",
    },
    "ContactType": {
        "type": "ComboBox",
        "pos": (frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "type",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ContactType';",
        "choicevalue": 0,
        "comparevalue": 1,
    },
    "lblContact": {
        "type": "StaticText",
        "label": "Contact:",
        "pos": (frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblContact",
    },
    "Contact": {
        "type": "StaticText",
        "pos": (frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Contact",
    },
    "lblUnlisted": {
        "type": "StaticText",
        "label": "Unlisted:",
        "pos": (frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblUnlisted",
    },
    "Unlisted": {
        "type": "CheckBox",
        "pos": (frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Unlisted",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmFamilyContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "value": "",
        "pos": (frmFamilyContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}
pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmFamilyContactFORM" : {
        "FORM": frmFamilyContactFORM,
        "CONTROLS": frmFamilyContactCONTROLS
    }
}

for f in frmFamilyContactCONTROLS:
    print (frmFamilyContactCONTROLS[f])
    pp.pprint(json.dumps(frmFamilyContactCONTROLS[f]))



# pp.pprint(Family)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmFamilyContact.json", "w")
f.write(newjson)
f.close()
