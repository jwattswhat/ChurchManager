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


frmHymnUsageDisplayCONST = {
    "FormWidth": 800,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 30,
    "FormColumn2": 150,
    "FormColumn3": 425,
    "Fieldheight": 30,
}
FormLineNumber = pos(30, frmHymnUsageDisplayCONST["FormHeight"], frmHymnUsageDisplayCONST["Fieldheight"])
frmHymnUsageDisplayFORM = {
    "type": "Frame",
    "title": "frmHymnUsageDisplay : HymnUsageDisplay",
    "pos": (10, 10),
    "size": (frmHymnUsageDisplayCONST["FormWidth"], frmHymnUsageDisplayCONST["FormHeight"]),
    "name": "frmHymnUsageDisplay",
    "tablename": "tblService",
    "SQL": "SELECT ID, DateTime /*tb:dvlHymnUsage */ FROM tblService;",
    "style": "CAPTION",
    "linkedform": {
        "frmHymnSearch": {
            "pos": (100, 100),
            "bindbtn": "btnHymnAdd",
            "controls": ["Close"],
            "style": "(wx.CAPTION), #| wx.STAY_ON_TOP)",
        },
        "frmHymnUsage": {
            "SQL": "SELECT * FROM tblHymnUsage WHERE ID = {ID};",
            "bindbtn": "btnHymnUpdate",
            "controls": ["Close", "Navigation"]},
    },
}
frmHymnUsageDisplayCONTROLS = {
    "lblService": {
        "type": "StaticText",
        "label": "Service:",
        "pos": (frmHymnUsageDisplayCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblService",
    },
    "DateTime": {
        "type": "TextCtrl",
        "pos": (frmHymnUsageDisplayCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valDateandTime",
        "name": "DateTime",
        "readonly": True,
    },
    "boxHymns": {
        "type": "StaticBox",
        "label": "Hymns",
        "pos": (10, FormLineNumber.nextline()),
        "size": (frmHymnUsageDisplayCONST["FormWidth"] - 20, frmHymnUsageDisplayCONST["FormButtonRow"] - 75),
    },
    "dvlHymnUsage": {
        "type": "DataViewListCtrl",
        "column": [("ID",1), ("UsedAs", 100), ("Hymn", 75), ("Title", 300), ("Note", 200)],
        "columnSQL": "SELECT ID, UsedAs, concat(HymnalPrefix,Hymn) as Hymn, Title, Note FROM vwHymnUsage WHERE ServiceID = {value};",
        "value": "ID",
        "pos": (25, FormLineNumber.nextline()),
        "size": (frmHymnUsageDisplayCONST["FormWidth"] - 40, frmHymnUsageDisplayCONST["FormButtonRow"] - 165),
        "name" : "dvlHymnUsage",
    },
    "btnHymnAdd": {
        "type": "Button",
        "label": "Add",
        "pos": (20, frmHymnUsageDisplayCONST["FormButtonRow"] - 60),
        "name": "btnHymnAdd",
    },
    "btnHymnUpdate" : {
        "type": "Button",
        "label": "Update",
        "pos": (110, frmHymnUsageDisplayCONST["FormButtonRow"] - 60),
        "name" : "btnHymnUpdate",
    },
    "btnHymnDelete": {
        "type":"Button",
        "label": "Delete",
        "pos": (200, frmHymnUsageDisplayCONST["FormButtonRow"] - 60),
        "name" : "btnHymnDelete",
    },
    "btnUpdateService": {
        "type":"Button",
        "label": "Update Service",
        "pos":(10, frmHymnUsageDisplayCONST["FormButtonRow"]),
        "name" : "btnUpdateService",
    }
}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmHymnUsageDisplay" : {
        "FORM": frmHymnUsageDisplayFORM,
        "CONTROLS": frmHymnUsageDisplayCONTROLS
    }
}

for f in frmHymnUsageDisplayCONTROLS:
    print (frmHymnUsageDisplayCONTROLS[f])
    pp.pprint(json.dumps(frmHymnUsageDisplayCONTROLS[f]))

# pp.pprint(Family)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmHymnUsageDisplay.json", "w")
f.write(newjson)
f.close()
