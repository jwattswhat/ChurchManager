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

frmUtilityMainCONST = {
    "FormWidth": 600,
    "FormHeight": 400,
    "FormColumn1": 20,
    "FormColumn2": 300,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmUtilityMainCONST["FormHeight"], frmUtilityMainCONST["Fieldheight"])
frmUtilityMainFORM = {
    "type": "Frame",
    "pos": (0, 0),
    "size": (frmUtilityMainCONST["FormWidth"], frmUtilityMainCONST["FormHeight"]),
    "title": "Church Manager - Utility (v0.1)",
    "name": "frmUtilityMain",
    "style": wx.CAPTION,
}

frmUtilityMainCONTROLS = {
    "btnEditConfig": {
        "type": "Button",
        "label": "Add/Edit/Delete Configurations",
        "pos": (frmUtilityMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnConfig",
    },
    "btnEditOption": {
        "type": "Button",
        "label": "Add/Edit/Delete Options",
        "pos": (frmUtilityMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnOptions",
    },
    "btnEditChoices": {
        "type": "Button",
        "label": "Add/Edit/Delete Choices",
        "pos": (frmUtilityMainCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "btnChoices",
    },
    "btnClose": {
        "type": "Button",
        "label": "Close",
        "pos": (
            frmUtilityMainCONST["FormWidth"] - 100,
            frmUtilityMainCONST["FormHeight"] - 100,
        ),
        "name": "btnClose",
    },
}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "frmUtilityFORM" : {
        "FORM": frmUtilityMainFORM,
        "CONTROLS": frmUtilityMainCONTROLS
    }
}

for f in frmUtilityMainCONTROLS:
    print (frmUtilityMainCONTROLS[f])
    pp.pprint(json.dumps(frmUtilityMainCONTROLS[f]))


newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".//Forms//frmUtility.json", "w")
f.write(newjson)
f.close()
