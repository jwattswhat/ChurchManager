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
frmHymnCONST = {
    "FormWidth": 620,
    "FormHeight": 400,
    "FormButtonRow": 400 - 75,
    "FormColumn1": 0,
    "FormColumn2": 80,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmHymnCONST["FormHeight"], frmHymnCONST["Fieldheight"])

frmHymnFORM = {
    "type": "Frame",
    "title": "frmHymn: Hymn Edit Form",
    "pos": (10, 10),
    "size": (frmHymnCONST["FormWidth"], frmHymnCONST["FormHeight"]),
    # 'style': 'test',
    "name": "frmHymn",
    "tablename": "tblHymn",
    "SQL": "SELECT * FROM tblHymn ORDER BY Hymn;",
    "style": wx.CAPTION,
}
frmHymnCONTROLS = {
    "lblHymnal": {
        "type": "StaticText",
        "label": "Hymnal:",
        "pos": (frmHymnCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblHymnal",
    },
    "HymnalID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Hymnal FROM tblHymnal;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT Hymnal FROM tblHymnal WHERE ID = {value};",
        "pos": (frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": "wx.CB_READONLY",
        "name": "HymnalID",
    },
    "lblHymn": {
        "type": "StaticText",
        "label": "Hymn:",
        "pos": (frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblHymnalID",
    },
    "Hymn": {
        "type": "TextCtrl",
        "pos": (frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Hymn",
    },
    "lblTitle": {
        "type": "StaticText",
        "label": "Title:",
        "pos": (frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblTitle",
    },
    "Title": {
        "type": "TextCtrl",
        "pos": (frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Title",
    },
    "lblBibleText": {
        "type": "StaticText",
        "label": "Bible Refs:",
        "pos": (frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblBitleText",
    },
    "BibleText": {
        "type": "TextCtrl",
        "pos": (frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "BibleText",
    },
    "lblCategory": {
        "type": "StaticText",
        "label": "Category:",
        "pos": (frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCategory",
    },
    "Category": {
        "type": "ComboBox",
        "pos": (frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Category",
        "style": "wx.CB_READONLY",
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'Category';",
        "choicevalue": 0,
        "comparevalue": 0,
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmHymnCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmHymnCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": "wx.TE_MULTILINE",
        "name": "Note",
    },
}

#


pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmFamilyFORM)
newform = {
    "PersonFORM" : {
        "FORM": frmHymnFORM,
        "CONTROLS": frmHymnCONTROLS
    }
}


# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".\\Forms\\frmHymn.json", "w")
f.write(newjson)
f.close()
