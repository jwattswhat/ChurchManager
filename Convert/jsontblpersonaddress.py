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


#
#   Church Table Form
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
    "pos": (10, 10),
    "size": (frmPersonAddressCONST["FormWidth"], frmPersonAddressCONST["FormHeight"]),
    "name": "frmPersonAddress",
    "tablename": "tblPersonAddress",
    "SQL": "SELECT * FROM tblPersonAddress;",
    "style": wx.CAPTION,
}
frmPersonAddressCONTROLS = {
    "lblPerson": {
        "type": "StaticText",
        "label": "Person:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPerson",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson;",
        "choicevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) as PersonID FROM tblPerson WHERE ID= {value};",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "lblLabel": {
        "type": "StaticText",
        "label": "Label:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLabel",
    },
    "AddressLabel": {
        "type": "ComboBox",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "AddressLabel",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'AddressLabel';",
        "choicevalue": 0,
    },
    "lblAddress": {
        "type": "StaticText",
        "label": "Address:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAddress:",
    },
    "Address": {
        "type": "TextCtrl",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Address",
    },
    "Address2": {
        "type": "TextCtrl",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.nextline()),
        "size": (300, 30),
        "name": "Address2",
    },
    "lblCity": {
        "type": "StaticText",
        "label": "City:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "City": {
        "type": "TextCtrl",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "City",
    },
    "lblState": {
        "type": "StaticText",
        "label": "City:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "State": {
        "type": "TextCtrl",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "State",
    },
    "lblZip": {
        "type": "StaticText",
        "label": "Zip:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblZip:",
    },
    "Zip": {
        "type": "TextCtrl",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Zip",
    },
    "lblStartDate": {
        "type": "StaticText",
        "label": "Start Date:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblStartDate",
    },
    "StartDate": {
        "type": "TextCtrl",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "StartDate",
    },
    "lblEndDate": {
        "type": "StaticText",
        "label": "End Date:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblEndDate",
    },
    "EndDate": {
        "type": "TextCtrl",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "EndDate",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmPersonAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmPersonAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "PersonAddressFORM" : {
        "FORM": frmPersonAddressFORM,
        "CONTROLS": frmPersonAddressCONTROLS
    }
}

for f in frmPersonAddressCONTROLS:
    print (frmPersonAddressCONTROLS[f])
    pp.pprint(json.dumps(frmPersonAddressCONTROLS[f]))


# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open("frmPersonAddress.json", "w")
f.write(newjson)
f.close()
