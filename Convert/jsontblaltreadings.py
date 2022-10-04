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
frmAltReadingCONST = {
    "FormWidth": 620,
    "FormHeight": 450,
    "FormButtonRow": 450 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmAltReadingCONST["FormHeight"], frmAltReadingCONST["Fieldheight"])

frmAltReadingFORM = {
    "type": "Frame",
    "title": "frmAltReading: AltReading Edit Form",
    "pos": (10, 10),
    "size": (frmAltReadingCONST["FormWidth"], frmAltReadingCONST["FormHeight"]),
    "name": "frmAltReading",
    "tablename": "tblAltReading",
    "SQL": "SELECT * FROM tblAltReading ORDER BY PropersID;",
    "style": wx.CAPTION,
}

frmAltReadingCONTROLS = {
    "plabels": {
        "type": "StaticText",
        "label": "            Yr Season Proper",  # <TODO> Yuck!
        "pos": (frmAltReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "name": "plabel",
    },
    "lblPropersID": {
        "type": "StaticText",
        "label": "Propers:",
        "pos": (frmAltReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblPropersID",
    },
    "PropersID": {
        "type": "TextCtrl",
        "pos": (frmAltReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "PropersID",
        "lkpSQL": "SELECT CONCAT( Series,' ',Season,' ',LiturgicalDate) FROM tblPropers WHERE ID = {value}",
        "readonly": True,
    },
    "lblAltReading": {
        "type": "StaticText",
        "label": "AltReading:",
        "pos": (frmAltReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAltReading",
    },
    "AltReading": {
        "type": "ComboBox",
        "pos": (frmAltReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "AltReading",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'AltReading';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblAltReadingReference": {
        "type": "StaticText",
        "label": "Reference:",
        "pos": (frmAltReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAltReadingReference",
    },
    "AltReadingReference": {
        "type": "TextCtrl",
        "pos": (frmAltReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "AltReadingReference",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note",
        "pos": (frmAltReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmAltReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "savestyle": "TE_MULTILINE",
        "name": "Note",
    },
}





pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmAltReadingFORM" : {
        "FORM": frmAltReadingFORM,
        "CONTROLS": frmAltReadingCONTROLS
    }
}

for f in frmAltReadingCONTROLS:
    print (frmAltReadingCONTROLS[f])
    pp.pprint(json.dumps(frmAltReadingCONTROLS[f]))



# pp.pprint(Family)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmAltReading.json", "w")
f.write(newjson)
f.close()
