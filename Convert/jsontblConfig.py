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


frmConfigCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 75,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmConfigCONST["FormHeight"], frmConfigCONST["Fieldheight"])
frmConfigFORM = {
    "type": "Frame",
    "title": "frmConfig: Config Edit Form",
    "pos": (10, 10),
    "size": (frmConfigCONST["FormWidth"], frmConfigCONST["FormHeight"]),
    "name": "frmConfig",
    "tablename": "tblConfig",
    "SQL": "SELECT * FROM tblConfig;",
    "style": wx.CAPTION,
}
frmConfigCONTROLS = {
    "lblConfigType": {
        "type": "StaticText",
        "label": "Type:",
        "pos": (frmConfigCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblConfigType",
    },
    "ConfigType": {
        "type": "ComboBox",
        "pos": (frmConfigCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'ConfigType';",
        "choicevalue": 1,
        "comparevalue": 0,
        "style": wx.CB_READONLY,
        "name": "ConfigType",
    },
    "lblConfigValue": {
        "type": "StaticText",
        "label": "Value:",
        "pos": (frmConfigCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblConfigValue",
    },
    "ConfigValue": {
        "type": "TextCtrl",
        "pos": (frmConfigCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "ConfigValue",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmConfigCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote:",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmConfigCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        "name": "Note",
    },
}


pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "ConfigFORM" : {
        "FORM": frmConfigFORM,
        "CONTROLS": frmConfigCONTROLS
    }
}

for f in frmConfigCONTROLS:
    print (frmConfigCONTROLS[f])
    pp.pprint(json.dumps(frmConfigCONTROLS[f]))


# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open("frmConfig.json", "w")
f.write(newjson)
f.close()
