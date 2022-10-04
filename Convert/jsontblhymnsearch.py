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


frmHymnSearchCONST = {
    "FormWidth": 1200,
    "FormHeight": 800,
    "FormButtonRow": 800 - 75,
    "FormColumn1": 10,
    "FormColumn2": 100,
    "FormColumn3": 475,
    "FormColumn4": 1175,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmHymnSearchCONST["FormHeight"], frmHymnSearchCONST["Fieldheight"])
frmHymnSearchFORM = {
    "type": "Frame",
    "title": "frmHymnSearch : Hymn Search Form",
    "pos": (20, 20),
    "size": (frmHymnSearchCONST["FormWidth"], frmHymnSearchCONST["FormHeight"]),
    "name": "frmHymnSearch",
    "style": "CAPTION",
}
frmHymnSearchCONTROLS = {
    "lblSearch": {
        "type": "StaticText",
        "label": "Search:",
        "pos": (frmHymnSearchCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblSearch",
    },
    "Search": {
        "type": "TextCtrl",
        "pos": (frmHymnSearchCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Search",
        "norecorddata": True,
    },
    "btnByHymn": {
        "type": "Button",
        "label": "By Hymn",
        "pos": (frmHymnSearchCONST["FormColumn1"], FormLineNumber.nextline()),
        "size": (100, 30),
        "name": "btnByHymn",
    },
    "btnByTitle": {
        "type": "Button",
        "label": "By Title",
        "pos": (frmHymnSearchCONST["FormColumn1"] + 100, FormLineNumber.sameline()),
        "size": (100, 30),
        "name": "btnByTitle",
    },
    "btnByBible": {
        "type": "Button",
        "label": "By Bible",
        "pos": (frmHymnSearchCONST["FormColumn1"] + 200, FormLineNumber.sameline()),
        "size": (100, 30),
        "name": "btnByBibile",
    },
    "btnByCategory": {
        "type": "Button",
        "label": "By Category",
        "pos": (frmHymnSearchCONST["FormColumn1"] + 300, FormLineNumber.sameline()),
        "size": (100, 30),
        "name": "btnByCategroy",
    },
    "btnByNote": {
        "type": "Button",
        "label": "By Note",
        "pos": (frmHymnSearchCONST["FormColumn1"] + 400, FormLineNumber.sameline()),
        "size": (100, 30),
        "name": "btnByNote",
    },
    "dvlHymnList": {
        "type": "DataViewListCtrl",
        "column": [
            ("ID", 0),
            ("Hymn", 75),
            ("Title", 300),
            ("BibleText", 300),
            ("Category", 200),
            ("Note", 300),
        ],
        "columnSQL": "SELECT ID, CONCAT(HymnalPrefix,Hymn) as Hymn,Title,BibleText,Category,Note FROM vwHymnList ORDER BY Hymn;",
        "value": "*",
        "pos": (frmHymnSearchCONST["FormColumn1"], FormLineNumber.nextline()),
        "size": (frmHymnSearchCONST["FormWidth"] - 40, frmHymnSearchCONST["FormButtonRow"] - 75),
    },
    "btnAdd": {
        "type": "Button",
        "label": "Add",
        "pos": (frmHymnSearchCONST["FormColumn1"], frmHymnSearchCONST["FormButtonRow"]),
        "size": (50, 30),
        "name": "btnAdd",
    },
}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "frmHymnSearchFORM" : {
        "FORM": frmHymnSearchFORM,
        "CONTROLS": frmHymnSearchCONTROLS
    }
}

for f in frmHymnSearchCONTROLS:
    print (frmHymnSearchCONTROLS[f])
    pp.pprint(json.dumps(frmHymnSearchCONTROLS[f]))


# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".//Forms//frmHymnSearch.json", "w")
f.write(newjson)
f.close()
