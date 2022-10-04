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


frmAttendanceCONST = {
    "FormWidth": 620,
    "FormHeight": 500,
    "FormButtonRow": 750 - 75,
    "FormColumn1": 0,
    "FormColumn2": 145,
    "FormColumn3": 500,
    "Fieldheight": 30,
}
FormLineNumber = pos(0, frmAttendanceCONST["FormHeight"], frmAttendanceCONST["Fieldheight"])

frmAttendanceFORM = {
    "type": "Frame",
    "title": "frmAttendance : Service Edit Form",
    "pos": (10, 10),
    "size": (frmAttendanceCONST["FormWidth"], frmAttendanceCONST["FormHeight"]),
    "name": "frmAttendance",
    "tablename": "tblAttendance",
    "SQL": "SELECT * FROM tblAttendance ORDER BY DateTime DESC;",
    "style": wx.CAPTION,
}
frmAttendanceCONTROLS = {
    "lblPersonID": {
        "type": "StaticText",
        "label": "Person ID :",
        "pos": (frmAttendanceCONST["FormColumn1"], FormLineNumber.sameline()),
        "name": "lblPersonID",
    },
    "PersonID": {
        "type": "ComboBox",
        "choicesSQL": "SELECT ID, CONCAT(LastName,', ',FirstName) FROM tblPerson;",
        "choicevalue": 0,
        "lkpSQL": "SELECT CONCAT(LastName,', ',FirstName) FROM tblPerson WHERE ID={value};",
        "pos": (frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "style": wx.CB_READONLY,
        "name": "PersonID",
    },
    "lblAttendanceEventID": {
        "type": "StaticText",
        "label": "Attenandance Event ID:",
        "pos": (frmAttendanceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAttendanceEventID",
    },
    "AttendanceEventID": {
        "type": "TextCtrl",
        "pos": (frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "AttendanceID",
    },
    "lblDateTime": {
        "type": "StaticText",
        "label": "Attendance Date: ",
        "pos": (frmAttendanceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblDateTime",
    },
    "DateTime": {
        "type": "TextCtrl",
        "pos": (frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "DateTime",
        "validator": "valDateandTime",
    },
    "lblAttendanceTypeID": {
        "type": "StaticText",
        "label": "Attendance Type ID:",
        "pos": (frmAttendanceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblAttendanceTypeID",
    },
    "AttendanceTypeID": {
        "type": "TextCtrl",
        "pos": (frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 30),
        "name": "lblAttendanceTypeID",
    },
    "lblNote": {
        "type": "StaticText",
        "label": "Note:",
        "pos": (frmAttendanceCONST["FormColumn1"], FormLineNumber.nextline()),
        "name": "lblNote",
    },
    "Note": {
        "type": "TextCtrl",
        "pos": (frmAttendanceCONST["FormColumn2"], FormLineNumber.sameline()),
        "size": (300, 100),
        "style": wx.TE_MULTILINE,
        # 'validator': ,
        "name": "Note",
    },
}


pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(frmPersonFORM)
newform = {
    "AttendanceFORM" : {
        "FORM": frmAttendanceFORM,
        "CONTROLS": frmAttendanceCONTROLS
    }
}

for f in frmAttendanceCONTROLS:
    print (frmAttendanceCONTROLS[f])
    pp.pprint(json.dumps(frmAttendanceCONTROLS[f]))


# pp.pprint(person)
newjson = json.dumps(newform)
pp.pprint(newjson)
f = open(".//Forms//frmAttendance.json", "w")
f.write(newjson)
f.close()
