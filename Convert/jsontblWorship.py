import pprint
import json
import wx
FORMColors = {
    "Warning": {"fcolor": "White", "bcolor": "Red"},
    "Error": {"fcolor": "White", "bcolor": "Red"},
    "Notice": {"fcolor": "Blue", "bcolor": "White"},
    "Normal": {"fcolor": "Black", "bcolor": "White"},
}

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

frmServiceCONST = {
    "FormWidth": 1300,
    "FormHeight": 900,
    "FormButtonRow": 900 - 75,
    "FormColumn1": 0,
    "FormColumn2": 145,
    "FormColumn3": 475,
    "FormColumn4": 1175,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmServiceCONST["FormHeight"], frmServiceCONST["Fieldheight"])
frmServiceFORM = {
    "type": "Panel",
    "title": "frmService : Service Edit Form",
    "pos": (20, 20),
    "size": (frmServiceCONST["FormWidth"], frmServiceCONST["FormHeight"]),
    "name": "frmService",
    "tablename": "tblService",
    "SQL": "SELECT * FROM tblService ORDER BY DateTime DESC;",
    "stylelist": ["CAPTION"],
    "linkedform": {
        "frmHymnUsageDisplay": {
            "pos": (frmServiceCONST["FormWidth"] - 350, 100),
            "SQL": "SELECT ID, DateTime /*tb:dvlHymnUsage*/ FROM tblService WHERE ID = {ID};",
            "controls": ["Close"],
            "bindbtn": "btnHymns",
            "stylelist": ["CAPTION","STAYONTOP"],
        },
        "frmAltReadingsDisplay": {
            "pos": (frmServiceCONST["FormColumn3"] + 300, frmServiceCONST["FormHeight"] + 100),
            "SQL": "SELECT * FROM tblService WHERE ID = {ID};",
            "controls": ["Close"],
            "bindbtn": "btnAtlReadings",
            "stylelist": ["CAPTION","STAYONTOP"],
        },
    },
    "subform": {
        "frmPropers": {
            "type": "StaticBox",
            "label": "Propers",
            "pos": (frmServiceCONST["FormColumn3"], 10),
            "SQL": "SELECT Lectionary,Sort,Series,Season,LiturgicalDate,CalendarDateFrom,CalendarDateTo,Color FROM tblPropers WHERE ID = {PropersID};",
            "controls": [],
            "readonly": True,
        },
        "frmReadingList": {
            "type": "StaticBox",
            "label": "Readings",
            "SQL": "SELECT ID /*tb:dvlReadings*/ FROM tblPropers WHERE ID={ID};",
            "pos": (frmServiceCONST["FormColumn3"], frmServiceCONST["FormHeight"] + 10),
            "controls": [],
            "readonly": True,
            "stylelist": ["CAPTION","STAYONTOP"],
        },
    },
}
frmServiceCONTROLS = {
    "lblLectionary": {
        "type": "StaticText",
        "label": "Lectionary:",
        "pos": (5, FormLineNumber.sameline()),
        "name": "lblLectionary",
    },
    "lblYear": {
        "type": "StaticText",
        "label": "Year",
        "pos": (100, FormLineNumber.sameline()),
        "name": "lblYear",
    },
    "lblToday": {
        "type": "StaticText",
        "label": "Today's Date",
        "pos": (145, FormLineNumber.sameline()),
        "name": "lblToday",
    },
    "Lectionary": {
        "type": "StaticText",
        "fcolor": FORMColors["Notice"]["fcolor"],
        "bcolor": FORMColors["Notice"]["bcolor"],
        "pos": (15, FormLineNumber.nextline() - 10),
        "lkpSQL": "SELECT ConfigValue FROM tblConfig WHERE ConfigType = 'Lectionary';",
        "Name": "Lectionary",
    },
    "LectionarySeriesYear": {
        "type": "StaticText",
        "fcolor": "BLUE",
        "pos": (100, FormLineNumber.sameline() - 10),
        "lkpSQL": "SELECT ConfigValue FROM tblConfig WHERE ConfigType = 'LectionarySeriesYear';",
        "Name": "LectionarySeriesYear",
    },
    "Today": {
        "type": "StaticText",
        "fcolor": "BLUE",
        "date": "today",
        "pos": (145, FormLineNumber.sameline() - 10),
        "Name": "lblToday",
    },
    "btnHymns": {
        "type": "Button",
        "label": "Hymns",
        "pos": (frmServiceCONST["FormColumn4"], FormLineNumber.sameline()),
        "size": (100, 30),
        "name": "btnNew",
    },
    "lblChurchID": {
        "type": "StaticText",
        "label": "Church :",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblChurchID",
    },
    "ChurchID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, Church FROM tblChurch;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT Church FROM tblChurch WHERE ID={value};",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "stylelist": ["READONLY"],
        "name": "ChurchID",
    },
    "lblDateTime": {
        "type": "StaticText",
        "label": "Service Date/Time:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblServiceDateTime",
    },
    "DateTime": {
        "type": "TextCtrl",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "validator": "valDateandTime",
        "name": "DateTime",
    },
    "lblPropersID": {
        "type": "StaticText",
        "label": "Propers:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblPropersID",
    },
    "PropersID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(Series,' ',Season,' ',LiturgicalDate) FROM tblPropers ORDER BY Sort;",
        "choicevalue": 1,
        "comparevalue": 0,
        "lkpSQL": "SELECT CONCAT(Series,' ',Season,' ',LiturgicalDate) FROM tblPropers  WHERE ID={value} ORDER BY Sort;",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "stylelist": ["READONLY"],
        "name": "PropersID",
    },
    "lblLiturgicalDate": {
        "type": "StaticText",
        "label": "Liturgical Date:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblLiturgicalDate",
    },
    "LiturgicalDate": {
        "type": "TextCtrl",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "LiturgicalDate",
    },
    "lblHolyCommunion": {
        "type": "StaticText",
        "label": "Holy Communion:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblHolyCommunion",
    },
    "HolyCommunion": {
        "type": "CheckBox",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "HolyCommunion",
    },
    "lblOrderofServiceID": {
        "type": "StaticText",
        "label": "OrderofService:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblOrderofService",
    },
    "OrderofServiceID": {
        "type": "TextCtrl",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "OrderofServiceID",
    },
    "lblOSNote": {
        "type": "StaticText",
        "label": "OSNote:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblOSNote",
    },
    "OSNote": {
        "type": "TextCtrl",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 130),
        "stylelist": ["MULTILINE"],
        "name": "OSNote",
    },
    "lblPsalmorIntroit": {
        "type": "StaticText",
        "label": "Psalm or Introit:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline(100)),
        "name": "lblPsalmorIntroit",
    },
    "PsalmorIntroit": {
        "type": "ComboBox",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "PsalmorIntroit",
        "stylelist": ["READONLY"],
        "choicesSQL": "SELECT Choices FROM tblChoices WHERE Field = 'PsalmorIntroit';",
        "comparevalue": 0,
        "choicevalue": 0,
    },
    "lblSermonText": {
        "type": "StaticText",
        "label": "Sermon:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblSermonText",
    },
    "SermonText": {
        "type": "TextCtrl",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "SermonText",
    },
    "lblBulletin": {
        "type": "StaticText",
        "label": "Bulletin:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblBulletin",
    },
    "Bulletin": {
        "type": "TextCtrl",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Bulletin",
    },
    "btnAtlReadings": {
        "type": "Button",
        "label": "Alt Readings",
        "pos": (frmServiceCONST["FormColumn4"], FormLineNumber.sameline()),
        "size": (100, 30),
        "name": "btnNew",
    },
    "lblInserts": {
        "type": "StaticText",
        "label": "Inserts:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblInserts",
    },
    "Inserts": {
        "type": "TextCtrl",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "Inserts",
    },
    "lblCheckListComplete": {
        "type": "StaticText",
        "label": "Check List Complete:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCheckListComplete",
    },
    "CheckListComplete": {
        "type": "CheckBox",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "CheckListComplete",
    },
    "lblCheckListID": {
        "type": "StaticText",
        "label": "Check List ID:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCheckListID",
    },
    "CheckListID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CheckListName FROM tblCheckList;",
        "comparevalue": 0,
        "choicevalue": 1,
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "CheckListID",
    },
    "lblCheckList": {
        "type": "StaticText",
        "label": "CheckList:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblCheckList",
    },
    "CheckList": {
        "type": "CheckListBox",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 130),
        "name": "CheckList",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmServiceCONST["FormColumn1"], FormLineNumber.nextline(100)),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmServiceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "stylelist": ["MULTILINE"],
        "name": "Note",
    },
}


pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "frmUtilityFORM" : {
        "FORM": frmServiceFORM,
        "CONTROLS": frmServiceCONTROLS
    }
}

for f in frmServiceCONTROLS:
    print (frmServiceCONTROLS[f])
    pp.pprint(json.dumps(frmServiceCONTROLS[f]))


newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".//Forms//frmService.json", "w")
f.write(newjson)
f.close()
