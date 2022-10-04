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

frmReadingListCONST = {
    "FormWidth": 800,
    "FormHeight": 350,
    "FormButtonRow": 350 - 75,
    "FormColumn1": 30,
    "FormColumn2": 150,
    "FormColumn3": 425,
    "Fieldheight": 30,
}
FormLineNumber = pos(30, frmReadingListCONST["FormHeight"], frmReadingListCONST["Fieldheight"])
frmReadingListFORM = {
    "type": "Frame",
    "title": "frmReadingList : ReadingsDisplay",
    "subformtype": "StaticBox",
    "label": "Readings",
    "pos": (10, 10),
    "size": (frmReadingListCONST["FormWidth"], frmReadingListCONST["FormHeight"]),
    "name": "frmReadingList",
    "tablename": "tblPropers",
    #"SQL": "SELECT ID /*tb:dvlReadings*/ FROM tblPropers WHERE ID={ID};",
    "stylelist": ["CAPTION"],
}
frmReadingListCONTROLS = {
    "dvlReadings": {
        "type": "DataViewListCtrl",
        "column": [("Reading", 100), ("ReadingReference", 300), ("Note", 100)],
        "columnSQL": "SELECT Reading, ReadingReference, Note FROM tblReading WHERE PropersID = {value};",
        "value": "ID",
        "pos": (25, 30),
        "size": (frmReadingListCONST["FormWidth"] - 40, frmReadingListCONST["FormHeight"] - 100),
    },
}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "frmUtilityFORM" : {
        "FORM": frmReadingListFORM,
        "CONTROLS": frmReadingListCONTROLS
    }
}

for f in frmReadingListCONTROLS:
    print (frmReadingListCONTROLS[f])
    pp.pprint(json.dumps(frmReadingListCONTROLS[f]))


newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".//Forms//frmReadingList.json", "w")
f.write(newjson)
f.close()
