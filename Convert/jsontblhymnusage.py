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

frmHymnUsageCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 150,
    "Fieldheight": 30,
    "FieldPos": pos(0, 400, 30),  # (formheight, fieldheight)
}
FormLineNumber = pos(0, frmHymnUsageCONST["FormHeight"], frmHymnUsageCONST["Fieldheight"])
frmHymnUsageFORM = {
    "type": "Frame",
    "title": "frmHymnUsage: Hymn Usage Edit Form",
    "pos": (10, 10),
    "size": (frmHymnUsageCONST["FormWidth"], frmHymnUsageCONST["FormHeight"]),
    "name": "frmHymnUsage",
    "tablename": "tblHymnUsage",
    "SQL": "SELECT * FROM tblHymnUsage ORDER BY ServiceID;",
    "stylelist": ["CAPTION"],
}
frmHymnUsageCONTROLS = {
    "lblServiceID": {
        "type": "StaticText",
        "label": "Service Date/Time:",
        "pos": (frmHymnUsageCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblServiceID",
    },
    "ServiceID": {
        "type": "TextCtrl",
        "pos": (frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "ServiceID",
        "lkpSQL": "SELECT DateTime FROM tblService WHERE ID = {value}",
        "readonly": True,
    },
    "lblHymnID": {
        "type": "StaticText",
        "label": "Hymn:",
        "pos": (frmHymnUsageCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblHymnID",
    },
    "HymnID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT h.ID,concat(hl.HymnalPrefix, h.Hymn, ' ', h.Title) FROM tblHymnal hl JOIN tblHymn h ON h.HymnalID = hl.ID",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT concat(hl.HymnalPrefix, h.Hymn, ' ', h.Title) FROM tblHymnal hl JOIN tblHymn h ON h.HymnalID = hl.ID WHERE h.ID = {value};",
        "pos": (frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "stylelist": ["CB_READONLY"],
        "name": "HymnID",
    },
    "lblHymnUsageTypeID": {
        "type": "StaticText",
        "label": "Hymn Usage Type ID:",
        "pos": (frmHymnUsageCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblHymnUsageTypeID",
    },
    "HymnUsageTypeID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, UsedAs FROM tblHymnUsageType;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT UsedAs FROM tblHymnUsageType WHERE ID = {value};",
        "pos": (frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "stylelist": ["CB_READONLY"],
        "name": "HymnUsageTypeID",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note",
        "pos": (frmHymnUsageCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmHymnUsageCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "stylelist": ["TE_MULTILINE"],
        "name": "Note",
    },
}


pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmHymnUsage" : {
        "FORM": frmHymnUsageFORM,
        "CONTROLS": frmHymnUsageCONTROLS
    }
}


# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmHymnUsage.json", "w")
f.write(newjson)
f.close()
