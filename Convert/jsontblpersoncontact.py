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
    "pos": (10, 10),
    "size": (frmPersonContactCONST["FormWidth"], frmPersonContactCONST["FormHeight"]),
    "name": "frmPersonContact",
    "tablename": "tblPersonContact",
    "SQL": "SELECT * FROM tblPersonContact;",
    "style": wx.CAPTION,
}
frmPersonContactCONTROLS = {
    "lblPerson": {
        "type": "StaticText",
        "label": "Person:",
        "pos": (frmPersonContactCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPerson",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson WHERE ID={value};",
        "pos": (frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "lblLabel": {
        "type": "StaticText",
        "label": "Label:",
        "pos": (frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLabel",
    },
    "ContactLabel": {
        "type": "TextCtrl",
        "pos": (frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "ContactLabel",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ContactLabel';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": (frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblType",
    },
    "ContactType": {
        "type": "ComboBox",
        "pos": (frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "type",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ContactType';",
        "choicevalue": 0,
        "comparevalue": 0
    },
    "lblContact": {
        "type": "StaticText",
        "label": "Contact:",
        "pos": (frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblContact",
    },
    "Contact": {
        "type": "TextCtrl",
        "pos": (frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Contact",
    },
    "lblUnlisted": {
        "type": "StaticText",
        "label": "Unlisted:",
        "pos": (frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblUnlisted",
    },
    "Unlisted": {
        "type": "CheckBox",
        "pos": (frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Unlisted",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmPersonContactCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmPersonContactCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "PersonContactFORM" : {
        "FORM": frmPersonContactFORM,
        "CONTROLS": frmPersonContactCONTROLS
    }
}

for f in frmPersonContactCONTROLS:
    print (frmPersonContactCONTROLS[f])
    pp.pprint(json.dumps(frmPersonContactCONTROLS[f]))



# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open("frmPersonContact.json", "w")
f.write(newjson)
f.close()
