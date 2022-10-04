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

frmMembershipMainCONST = {
    "FormWidth": 600,
    "FormHeight": 500,
    "FormColumn1": 10,
    "FormColumn2": 300,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmMembershipMainCONST["FormHeight"], frmMembershipMainCONST["Fieldheight"])
frmMembershipMainFORM = {
    "type": "Frame",
    "pos": (0, 0),
    "size": (frmMembershipMainCONST["FormWidth"], frmMembershipMainCONST["FormHeight"]),
    "title": "Church Manager - Membership (v0.1)",
    "name": "frmMembershipMain",
    "style": wx.CAPTION,
}
frmMembershipMainCONTROLS = {
    "btnEditChurch": {
        "type": "Button",
        "label": "Add/Edit/Delete Church",
        "pos": (frmMembershipMainCONST["FormColumn1"], FormLineNumber.nextline()),
        # 'size': (0, 0),
        "name": "btnEditChurch",
    },
    "btnEditPerson": {
        "type": "Button",
        "label": "Add/EditDelete Person",
        "pos": (frmMembershipMainCONST["FormColumn1"], FormLineNumber.skipline()),
        "name": "btnEditPerson",
    },
    "btnEditPersonAddress": {
        "type": "Button",
        "label": "Add/Edit/Delete Person Address",
        "pos": (frmMembershipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
        "name": "btnEditPersonAddress",
    },
    "btnEditPersonContact": {
        "type": "Button",
        "label": "Add/Edit/Delete Person Contact",
        "pos": (frmMembershipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
        "name": "btnEditPersonContact",
    },
    "btnEditPersonDate": {
        "type": "Button",
        "label": "Add/Edit/Delete Person Date",
        "pos": (frmMembershipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
        "name": "btnEditPersonDate",
    },
#    "btnEditPersonDateGrid": {
#        "type": "Button",
#        "label": "Person Date Grid",
#        "pos": (frmMembershipMainCONST["FormColumn1"] + 20, FormLineNumber.nextline()),
#        "name": "btnEditPersonDateGrid",
#    },
    "btnEditFamily": {
        "type": "Button",
        "label": "Add/Edit/Delete Family",
        "pos": (frmMembershipMainCONST["FormColumn2"], FormLineNumber.reset(105)),
        "name": "btnEditFamily",
    },
    "btnEditFamilyAddress": {
        "type": "Button",
        "label": "Add/Edit/Delete Family Address",
        "pos": (frmMembershipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditFamilyAddress",
    },
    "btnEditFamilyContact": {
        "type": "Button",
        "label": "Add/Edit/Delete Family Contact",
        "pos": (frmMembershipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditFamilyContact",
    },
    "btnEditFamilyDate": {
        "type": "Button",
        "label": "Add/Edit/Delete Family Date",
        "pos": (frmMembershipMainCONST["FormColumn2"] + 20, FormLineNumber.nextline()),
        "name": "btnEditFamilyDate",
    },
    "btnClose": {
        "type": "Button",
        "label": "Close",
        "pos": (
            frmMembershipMainCONST["FormWidth"] - 100,
            frmMembershipMainCONST["FormHeight"] - 100,
        ),
        "name": "btnClose",
    },
}




pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "frmMembershipMainFORM" : {
        "FORM": frmMembershipMainFORM,
        "CONTROLS": frmMembershipMainCONTROLS
    }
}

#for f in frmMembershipMainCONTROLS:
#    print (frmMembershipMainCONTROLS[f])
#    pp.pprint(json.dumps(frmMembershipMainCONTROLS[f]))

pp.pprint(newform)

# pp.pprint(Family)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmMembershipMain.json", "w")
f.write(newjson)
f.close()
