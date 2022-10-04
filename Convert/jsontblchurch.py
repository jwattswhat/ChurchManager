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
    "pos": [10, 10],
    "size":(frmChurchCONST["FormWidth"], frmChurchCONST["FormHeight"]),
    "name": "frmChurch",
    "tablename": "tblChurch",
    "SQL": "SELECT * FROM tblChurch ORDER BY Church;",
    "style": wx.CAPTION,
}

frmChurchCONTROLS = {
    "lblChurch": {
        "type": "StaticText",
        "label": "Church:",
        "pos": (frmChurchCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblChurch",
        "bindmouse": "wx.EVT_LEFT_DCLICK",
    },
    "Church": {
        "type": "TextCtrl",
        "value": "",
        "pos": (frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valNotNUll",
        "name": "Church",
    },
    "lblAddress": {
        "type": "StaticText",
        "label": "Address:",
        "pos": (frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAddress:",
    },
    "Address": {
        "type": "TextCtrl",
        "pos": (frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valNotNUll",
        "name": "Address",
    },
    "Address2": {
        "type": "TextCtrl",
        "pos": (frmChurchCONST["FormColumn2"], FormLineNumber.nextline()),
        "size": (300, 30),
        "name": "Address2",
    },
    "lblCity": {
        "type": "StaticText",
        "label": "City:",
        "pos": (frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "City": {
        "type": "TextCtrl",
        "value": "",
        "pos": (frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valNotNUll",
        "name": "City",
    },
    "lblState": {
        "type": "StaticText",
        "label": "State:",
        "pos": (frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCity:",
    },
    "State": {
        "type": "TextCtrl",
        "pos": (frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valNotNUll",
        "name": "State",
    },
    "lblZip": {
        "type": "StaticText",
        "label": "Zip:",
        "pos": (frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblZip:",
    },
    "Zip": {
        "type": "TextCtrl",
        "pos": (frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valLen5",
        "name": "Zip",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmChurchCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmChurchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    }
}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
churchform = {
    "ChurchFORM" : {
        "FORM": frmChurchFORM,
        "CONTROLS": frmChurchCONTROLS
    }
}

for f in frmChurchCONTROLS:
    print (frmChurchCONTROLS[f])
    pp.pprint(json.dumps(frmChurchCONTROLS[f]))



# pp.pprint(person)
churchjson = json.dumps(churchform)
pp.pprint(churchjson)
f = open("frmChurch.json", "w")
f.write(churchjson)
f.close()
