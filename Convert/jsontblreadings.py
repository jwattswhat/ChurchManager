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
frmReadingCONST = {
    "FormWidth": 620,
    "FormHeight": 450,
    "FormButtonRow": 450 - 75,
    "FormColumn1": 0,
    "FormColumn2": 125,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmReadingCONST["FormHeight"], frmReadingCONST["Fieldheight"])

frmReadingFORM = {
    "type": "Frame",
    "title": "frmReading: Reading Edit Form",
    "pos": (10, 10),
    "size": (frmReadingCONST["FormWidth"], frmReadingCONST["FormHeight"]),
    "name": "frmReading",
    "tablename": "tblReading",
    "SQL": "SELECT * FROM tblReading ORDER BY ReadingID;",
    "style": wx.CAPTION,
}

frmReadingCONTROLS = {
    "plabels": {
        "type": "StaticText",
        "label": "            Yr Season Proper",  # <TODO> Yuck!
        "pos": (frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "name": "plabel",
    },
    "lblReadingID": {
        "type": "StaticText",
        "label": "Reading:",
        "pos": (frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblReadingID",
    },
    "ReadingID": {
        "type": "TextCtrl",
        "pos": (frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "ReadingID",
        "lkpSQL": "SELECT CONCAT( Series,' ',Season,' ',LiturgicalDate) FROM tblReading WHERE ID = {value}",
        "readonly": True,
    },
    "lblReading": {
        "type": "StaticText",
        "label": "Reading:",
        "pos": (frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblReading",
    },
    "Reading": {
        "type": "ComboBox",
        "pos": (frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Reading",
        "style": wx.CB_READONLY,
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Reading';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblReadingReference": {
        "type": "StaticText",
        "label": "Reference:",
        "pos": (frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblReadingReference",
    },
    "ReadingReference": {
        "type": "TextCtrl",
        "pos": (frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "ReadingReference",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note",
        "pos": (frmReadingCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmReadingCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "savestyle": "TE_MULTILINE",
        "name": "Note",
    },
}





pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmReadingFORM" : {
        "FORM": frmReadingFORM,
        "CONTROLS": frmReadingCONTROLS
    }
}

for f in frmReadingCONTROLS:
    print (frmReadingCONTROLS[f])
    pp.pprint(json.dumps(frmReadingCONTROLS[f]))



# pp.pprint(Family)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmReading.json", "w")
f.write(newjson)
f.close()
