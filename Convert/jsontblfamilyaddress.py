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
    "pos": (10, 10),
    "size": (frmFamilyAddressCONST["FormWidth"], frmFamilyAddressCONST["FormHeight"]),
    "name": "frmFamilyAddress",
    "tablename": "tblFamilyAddress",
    "SQL": "SELECT * FROM tblFamilyAddress;",
    "style": wx.CAPTION,
}

frmFamilyAddressCONTROLS = {
    "lblFamilyID": {
        "type": "StaticText",
        "label": "Family:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblFamilyID",
    },
    "FamilyID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, FamilyName FROM tblFamily;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT FamilyName FROM tblFamily WHERE ID={value};",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "FamilyID",
    },
    "lblLabel": {
        "type": "StaticText",
        "label": "Label:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLabel",
    },
    "AddressLabel": {
        "type": "ComboBox",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "AddressLabel",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'AddressLabel';",
        "choicevalue": 0,
        "comparevalue": 0
    },
    "lblAddress": {
        "type": "StaticText",
        "label": "Address:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAddress:",
    },
    "Address": {
        "type": "TextCtrl",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valNotNUll",
        "name": "Address",
    },
    "Address2": {
        "type": "TextCtrl",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.nextline()),
        "size": (300, 30),
        "name": "Address2",
    },
    "lblCity": {
        "type": "StaticText",
        "label": "City:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "City": {
        "type": "TextCtrl",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valNotNUll",
        "name": "City",
    },
    "lblState": {
        "type": "StaticText",
        "label": "City:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "State": {
        "type": "TextCtrl",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valNotNUll",
        "name": "State",
    },
    "lblZip": {
        "type": "StaticText",
        "label": "Zip:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblZip:",
    },
    "Zip": {
        "type": "TextCtrl",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valLen5",
        "name": "Zip",
    },
    "lblStartDate": {
        "type": "StaticText",
        "label": "Start Date:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblStartDate",
    },
    "StartDate": {
        "type": "TextCtrl",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valDateAndNull",
        "name": "StartDate",
    },
    "lblEndDate": {
        "type": "StaticText",
        "label": "End Date:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblEndDate",
    },
    "EndDate": {
        "type": "TextCtrl",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valDateAndNull",
        "name": "EndDate",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmFamilyAddressCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmFamilyAddressCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}


pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "frmFamilyAddressFORM" : {
        "FORM": frmFamilyAddressFORM,
        "CONTROLS": frmFamilyAddressCONTROLS
    }
}

for f in frmFamilyAddressCONTROLS:
    print (frmFamilyAddressCONTROLS[f])
    pp.pprint(json.dumps(frmFamilyAddressCONTROLS[f]))


# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".//Forms//frmFamilyAddress.json", "w")
f.write(newjson)
f.close()
