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


frmPersonCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 500 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
    "FieldPos": pos(0, 525, 30),
}
FormLineNumber = pos(
    0, frmPersonCONST["FormHeight"], frmPersonCONST["Fieldheight"])

frmPersonFORM = {
    "type": "Frame",
    "title": "frmPerson : Person Edit Form",
    "pos": [10, 10],
    "size": (frmPersonCONST["FormWidth"], frmPersonCONST["FormHeight"]),
    "name": "frmPerson",
    "tablename": "tblPerson",
    "SQL": "SELECT ID,ChurchID,FamilyID,FirstName,MiddleName,LastName,Status,Baptized,Confirmed,Member,AssociateMember,Picture, Note FROM tblPerson ORDER BY LastName",
    "style": wx.CAPTION,
}
frmPersonCONTROLS = {
    "lblChurchID": {
        "type": "StaticText",
        "label": "Church:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblChurchID",
    },
    "ChurchID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Church FROM tblChurch;",
        "choicevalue": 0,
        "lkpSQL": "SELECT Church FROM tblChurch WHERE ID = {value};",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "ChurchID",
    },
    "lblFamilyID": {
        "type": "StaticText",
        "label": "Family:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblFamilyID",
    },
    "FamilyID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, FamilyName FROM tblFamily;",
        "choicevalue": 0,
        "lkpSQL": "SELECT FamilyName FROM tblFamily WHERE ID = {value};",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "FamilyID",
    },
    "lblFirstName": {
        "type": "StaticText",
        "label": "First Name:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblFirstName",
    },
    "FirstName": {
        "type": "TextCtrl",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "FirstName",
    },
    "lblMiddleName": {
        "type": "StaticText",
        "label": "Middle Name:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblMiddleName",
    },
    "MiddleName": {
        "type": "TextCtrl",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "MiddleName",
    },
    "lblLastName": {
        "type": "StaticText",
        "label": "Last Name:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLastName",
    },
    "LastName": {
        "type": "TextCtrl",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "LastName",
    },
    "lblStatus": {
        "type": "StaticText",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblStatus",
    },
    "Status": {
        "type": "ComboBox",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Status",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Status';",
        "choicevalue": 0,
    },
    "lblBaptized": {
        "type": "StaticText",
        "label": "Baptized:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblBaptized",
    },
    "Baptized": {
        "type": "CheckBox",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Baptized",
    },
    "lblConfirmed": {
        "type": "StaticText",
        "label": "Confirmed:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblConfirmed",
    },
    "Confirmed": {
        "type": "CheckBox",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Confirmed",
    },
    "lblMember": {
        "type": "StaticText",
        "label": "Member:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblMember",
    },
    "Member": {
        "type": "CheckBox",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Member",
    },
    "lblAssociateMember": {
        "type": "StaticText",
        "label": "Associate Member:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAssociateMember",
    },
    "AssociateMember": {
        "type": "CheckBox",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "AssociateMember",
    },
    #        "lblPicture" : {
    #        "Picture" : {
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmPersonCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmPersonCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "name": "Note",
        "style": wx.TE_MULTILINE,
    },
}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
personform = {
    "PersonFORM" : {
        "FORM": frmPersonFORM,
        "CONTROLS": frmPersonCONTROLS
    }
}


# pp.pprint(person)
personjson = json.dumps(personform)
pp.pprint(personjson)
f = open(".\\Forms\\frmPerson.json", "w")
f.write(personjson)
f.close()
