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


frmChoicesCONST = {
    "FormWidth": 620,
    "FormHeight": 550,
    "FormButtonRow": 550 - 75,
    "FormColumn1": 0,
    "FormColumn2": 100,
    "FormColumn3": 155,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmChoicesCONST["FormHeight"], frmChoicesCONST["Fieldheight"])
frmChoicesFORM = {
    "type": "Frame",
    "title": "frmChoices : Choices Edit Form",
    "pos": (10, 10),
    "size": (frmChoicesCONST["FormWidth"], frmChoicesCONST["FormHeight"]),
    "name": "frmChoices",
    "tablename": "tblChoices",
    "SQL": "SELECT * FROM tblChoices;",
    "style": wx.CAPTION,
}
frmChoicesCONTROLS = {
    "lblField": {
        "type": "StaticText",
        "label": "Field:",
        "pos": (frmChoicesCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblField",
    },
    "Field": {
        "type": "TextCtrl",
        "pos": (frmChoicesCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "Field",
    },
    "lblChoices": {
        "type": "StaticText",
        "label": "Choices:",
        "pos": (frmChoicesCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblChoices",
    },
    "Choices": {
        "type": "TextCtrl",
        "list": True,
        "pos": (frmChoicesCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 300),
        "style": wx.TE_MULTILINE,
        "name": "Choices",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmChoicesCONST["FormColumn1"], FormLineNumber.nextline(270)),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmChoicesCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}


pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "ChoicesFORM" : {
        "FORM": frmChoicesFORM,
        "CONTROLS": frmChoicesCONTROLS
    }
}

for f in frmChoicesCONTROLS:
    print (frmChoicesCONTROLS[f])
    pp.pprint(json.dumps(frmChoicesCONTROLS[f]))


# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".//Forms//frmChoices.json", "w")
f.write(newjson)
f.close()
