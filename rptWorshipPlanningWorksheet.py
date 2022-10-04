import os
from fpdf import FPDF
import argparse
import subprocess
from datetime import datetime
import json

import mysql
import mysql.connector

#   ChurchManager Classes
import clsDB
from clsConfig import CONFIG
from clsSQL import clsSQL


rpt_fontfamily = 0
rpt_fontstyle = 1
rpt_fontsize = 2
rpt_date = datetime.now().strftime("%d%b%Y")
rpt_time = datetime.now().strftime("%H%M")


class indent:
    def __init__(self, start, inc):
        self.value = start
        self.inc = inc

    def setstart(self, start, inc):
        self.value = start
        self.inc = inc

    def inn(self):
        self.value += self.inc
        return self.value

    def out(self):
        self.value -= self.inc
        return self.value

    def val(self):
        return self.value


class PDF(FPDF):
    ic = indent(10.0, 5.0)
    member_count = 0

    def setDocumentHeader(self, **kwargs):
        self.CHURCHNAME = kwargs["church"]
        self.HEADERTITLE = kwargs["titles"]
        self.HEADERFONT = kwargs["churchfont"]
        self.SUBHEADERFONT = kwargs["titlefont"]
        self.HEADERSIZE = kwargs["size"]
        self.REPORTDATE = kwargs["date"]

    def setDocumentFooter(self, **kwargs):
        self.FOOTERFONT = kwargs["font"]
        self.FOOTERSIZE = kwargs["size"]

    def setDefaultFont(self, **kwargs):
        self.DEFAULTFONT = {
            "family": kwargs["family"],
            "style": kwargs["style"],
            "size": kwargs["size"],
        }

    def setDefaultBoldFont(self, **kwargs):
        self.DEFAULTBOLDFONT = {
            "family": kwargs["family"],
            "style": kwargs["style"],
            "size": kwargs["size"],
        }

    def setFont(self, **kwargs):
        args = kwargs
        if "family" not in args:
            args.update({"family": self.DEFAULTFONT["family"]})
        if "style" not in args:
            args.update({"style": self.DEFAULTFONT["style"]})
        elif args["style"] == "Bold":
            args.update({"style": "B"})
        if "size" not in args:
            args.update({"size": self.DEFAULTFONT["size"]})
        self.set_font(args["family"], args["style"], args["size"])

    def header(self):
        self.setFont(**self.HEADERFONT)
        self.cell(0, 5, self.CHURCHNAME, ln=2, align="C")
        self.setFont(**self.SUBHEADERFONT)
        for tl in self.HEADERTITLE:
            if tl != None:
                self.cell(0, rptService["Header"]["lineheight"], tl, ln=2, align="C")
        self.cell(
            0, rptService["Header"]["lineheight"], self.REPORTDATE, ln=2, align="R"
        )

    def footer(self):
        self.setFont(**self.FOOTERFONT)
        self.set_y(-self.FOOTERSIZE)
        self.cell(
            0, rptService["Footer"]["lineheight"], str(self.page_no()), ln=2, align="C"
        )
        self.ln(20)

    def load_report_description(self, report):
        """
        loads form description from a JSON file.
        """
        global CONFIG

        ReportDescriptionLocation = CONFIG.get_Config_Value("Report", "Description")

        reportname = ReportDescriptionLocation + report + ".json"
        f = open(
            reportname,
        )
        return json.load(f)

    def print_service(self, service):
        if service == None:
            return
        self.ic.setstart(10.0, 5.0)

        if service._record == None:
            return

        # print heading

        self.ln(1)
        self.set_x(self.ic.inn())
        self.setFont(**{"style": "Bold", "size": 13})
        if service._record[0]["ServiceLiturgicalDate"] != None:
            self.cell(
                0,
                rptService["Body"]["lineheight"],
                txt=service._record[0]["ServiceLiturgicalDate"],
                ln=2,
                align="C",
            )
        if service._record[0]["Color"] != None:
            self.cell(
                0,
                rptService["Body"]["lineheight"],
                txt="Color: " + service._record[0]["Color"],
                ln=2,
                align="C",
            )
        if service._record[0]["DateTime"] != None:
            self.cell(
                0,
                rptService["Body"]["lineheight"],
                ln=2,
                txt=service._record[0]["DateTime"],
                align="C",
            )
        self.setFont()
        if service._record[0]["Theme"] != None:
            theme = "\n\r".join(service._record[0]["Theme"])
            self.multi_cell(0, 4, txt=theme, align="L", border=1)
            savey = self.get_y()

        savey = self.get_y()
        self.set_x(self.ic.val())
        column = self.get_string_width("Holy Communion: ")

        self.cell(
            column,
            rptService["Body"]["lineheight"],
            txt="Order of Service:",
            ln=0,
            align="L",
        )
        if service._record[0]["OrderofService"] != None:
            self.cell(
                rptService["Body"]["column1width"],
                rptService["Body"]["lineheight"],
                txt=service._record[0]["OrderofService"],
                ln=2,
                align="L",
            )
            self.set_x(self.ic.val())

        self.cell(
            column,
            rptService["Body"]["lineheight"],
            txt="Holy Communion:",
            ln=0,
            align="L",
        )
        if service._record[0]["HolyCommunion"] != None:
            self.cell(
                rptService["Body"]["column1width"],
                rptService["Body"]["lineheight"],
                txt=str(service._record[0]["HolyCommunion"]),
                ln=2,
                align="L",
            )
            self.set_x(self.ic.val())

        self.cell(
            column,
            rptService["Body"]["lineheight"],
            txt="Psalm/Introit:",
            ln=0,
            align="L",
        )
        if service._record[0]["PsalmorIntroit"] != None:
            self.cell(
                rptService["Body"]["column1width"],
                rptService["Body"]["lineheight"],
                txt=service._record[0]["PsalmorIntroit"],
                ln=2,
                align="L",
            )
            self.set_x(self.ic.inn())

        self.print_altreadings(column, service._record[0])
        self.set_x(self.ic.out())

        self.ln(rptService["Body"]["lineheight"])
        self.set_x(self.ic.val())

        self.set_x(self.ic.val())
        self.print_sermon(service._record[0])

        self.set_x(self.ic.val())

        self.cell(
            column,
            rptService["Body"]["lineheight"],
            txt="Bulletin:",
            ln=0,
            align="L",
        )
        if service._record[0]["Bulletin"] != None:
            self.cell(
                rptService["Body"]["column1width"],
                rptService["Body"]["lineheight"],
                txt=os.path.basename(service._record[0]["Bulletin"]),
                ln=2,
                align="L",
            )
        else:
            self.ln(rptService["Body"]["lineheight"])
        self.set_x(self.ic.val())

        #        self.cell(
        #            column,
        #            rptService["Body"]["lineheight"],
        #            txt="Insert:",
        #            ln=0,
        #            align="L",
        #        )
        #        if service._record[0]["InsertDocument"] != None:
        #            self.cell(
        #                rptService["Body"]["column1width"],
        #                rptService["Body"]["lineheight"],
        #                txt=service._record[0]["InsertDocument"],
        #                ln=2,
        #                align="L",
        #           )
        #        else:
        self.ln(rptService["Body"]["lineheight"])
        self.set_x(self.ic.val())

        self.print_hymns(0, service._record[0])

        self.print_roles(service._record[0])

        self.ln(rptService["Body"]["lineheight"])
        self.set_x(self.ic.val())

        self.set_x(self.ic.val())
        if service._record[0]["Note"] != None:
            note = "\n\r".join(service._record[0]["Note"])
            self.cell(0, self.get_string_width("Note"), txt="Note", ln=2, align="L")
            self.multi_cell(
                rptService["Body"]["column1width"],
                4,
                txt=note,
                align="L",
                border=1,
            )

        # beginning column 2 (Propers)

        self.set_y(savey)

        self.ic.setstart(rptService["Body"]["column2"], 5)
        self.set_x(self.ic.val())

        self.cell(
            column,
            rptService["Body"]["lineheight"],
            txt="Lectionary:",
            ln=0,
            align="L",
        )
        if service._record[0]["Lectionary"] != None:
            self.cell(
                rptService["Body"]["column1width"],
                rptService["Body"]["lineheight"],
                txt=str(service._record[0]["Lectionary"]),
                ln=2,
                align="L",
            )
        else:
            self.ln(rptService["Body"]["lineheight"])

        self.ic.setstart(rptService["Body"]["column2"], 5)
        self.set_x(self.ic.val())

        self.cell(
            column,
            rptService["Body"]["lineheight"],
            txt="Season:",
            ln=0,
            align="L",
        )
        if service._record[0]["Season"] != None:
            self.cell(
                rptService["Body"]["column1width"],
                rptService["Body"]["lineheight"],
                txt=str(service._record[0]["Season"]),
                ln=2,
                align="L",
            )
        else:
            self.ln(rptService["Body"]["lineheight"])

        self.ic.setstart(rptService["Body"]["column2"], 5)
        self.set_x(self.ic.val())

        self.cell(
            column,
            rptService["Body"]["lineheight"],
            txt="Color:",
            ln=0,
            align="L",
        )
        if service._record[0]["Lectionary"] != None:
            self.cell(
                rptService["Body"]["column1width"],
                rptService["Body"]["lineheight"],
                txt=str(service._record[0]["Color"]),
                ln=2,
                align="L",
            )
        else:
            self.ln(rptService["Body"]["lineheight"])

        self.ic.setstart(rptService["Body"]["column2"], 5)
        self.set_x(self.ic.val())

        self.print_readings(service._record[0])
        self.ln(1)

        self.ic.setstart(rptService["Body"]["column2"], 5)
        self.set_x(self.ic.val())
        if service._record[0]["Introit"] != None:
            introit = "\n\r".join(service._record[0]["Introit"])
            self.cell(
                0, self.get_string_width("Introit"), txt="Introit", ln=2, align="L"
            )
            self.multi_cell(0, 4, txt=introit, align="L", border=1)

    def print_readings(self, service):
        self.ln(rptService["Body"]["lineheight"])

        self.set_x(self.ic.val())
        self.cell(
            self.get_string_width("Readings"),
            rptService["Body"]["lineheight"],
            txt="Readings",
            ln=2,
            align="L",
        )
        self.set_x(self.ic.inn())
        sql = clsSQL(
            ChurchDBConnection, rptService["Body"]["Table"]["Readings"], service
        )
        SQL = sql.select()
        cursor = ChurchDBConnection.cursor()
        cursor.execute(SQL)
        rows = cursor.fetchall()
        for row in rows:
            self.set_x(self.ic.val())
            self.cell(
                self.get_string_width(row[0] + " : "),
                rptService["Body"]["lineheight"],
                txt=row[0] + " : ",
                ln=0,
                align="L",
            )
            self.cell(
                0,
                rptService["Body"]["lineheight"],
                txt=row[1],
                ln=2,
                align="L",
            )
        self.set_x(self.ic.out())

    def print_altreadings(self, labelwidth, service):
        sql = clsSQL(
            ChurchDBConnection, rptService["Body"]["Table"]["AltReading"], service
        )
        SQL = sql.select()
        cursor = ChurchDBConnection.cursor()
        cursor.execute(SQL)
        rows = cursor.fetchall()
        if len(rows) == 0:
            return
        self.ln(rptService["Body"]["lineheight"])
        for row in rows:
            self.set_x(self.ic.val())
            self.cell(
                labelwidth,
                rptService["Body"]["lineheight"],
                txt=row[0] + " : ",
                ln=0,
                align="L",
            )
            self.cell(
                rptService["Body"]["column1width"],
                rptService["Body"]["lineheight"],
                txt=row[1],
                ln=2,
                align="L",
            )

    def print_hymns(self, labelwidth, service):
        sql = clsSQL(
            ChurchDBConnection, rptService["Body"]["Table"]["HymnUsage"], service
        )
        SQL = sql.select()
        cursor = ChurchDBConnection.cursor()
        cursor.execute(SQL)
        rows = cursor.fetchall()
        if len(rows) == 0:
            return
        self.ln(rptService["Body"]["lineheight"])
        self.set_x(self.ic.val())
        self.cell(0, self.get_string_width("Note"), txt="Hymns", ln=2, align="L")
        for row in rows:
            self.set_x(self.ic.val())
            self.cell(
                self.get_string_width(row[0] + " "),
                rptService["Body"]["lineheight"],
                txt=row[0] + "-",
                ln=0,
                align="L",
            )
            self.cell(
                self.get_string_width("123456789x"),
                rptService["Body"]["lineheight"],
                txt=row[1] + " ",
                ln=0,
                align="L",
            )
            self.cell(
                self.get_string_width(row[2]),
                rptService["Body"]["lineheight"],
                txt=row[2],
                ln=2,
                align="L",
            )

    def print_sermon(self, service):
        if service["SermonID"] == None:
            return
        sql = clsSQL(ChurchDBConnection, rptService["Body"]["Table"]["Sermon"], service)
        SQL = sql.select()
        cursor = ChurchDBConnection.cursor()
        cursor.execute(SQL)
        row = cursor.fetchone()
        if len(row) == 0:
            return
        self.set_x(self.ic.val())
        self.cell(
            self.get_string_width("Sermon: "),
            rptService["Body"]["lineheight"],
            txt="Sermon:",
            ln=0,
            align="L",
        )
        self.cell(
            rptService["Body"]["column1width"],
            rptService["Body"]["lineheight"],
            txt=str(row[0]) + "-" + str(row[1]),
            ln=2,
            align="L",
        )

    def print_roles(self, service):
        sql = clsSQL(
            ChurchDBConnection, rptService["Body"]["Table"]["ServiceRole"], service
        )
        SQL = sql.select()
        cursor = ChurchDBConnection.cursor()
        cursor.execute(SQL)
        rows = cursor.fetchall()
        if len(rows) == 0:
            return
        self.ln(rptService["Body"]["lineheight"])
        self.set_x(self.ic.val())
        self.cell(0, self.get_string_width("Note"), txt="Participants", ln=2, align="L")
        for row in rows:
            self.set_x(self.ic.val())
            self.cell(
                self.get_string_width(row[0] + " "),
                rptService["Body"]["lineheight"],
                txt=row[0] + "-",
                ln=0,
                align="L",
            )
            self.cell(
                self.get_string_width(row[1]),
                rptService["Body"]["lineheight"],
                txt=row[1],
                ln=2,
                align="L",
            )


def create_sql_views():
    sql = "DROP VIEW IF EXISTS vwservicewithpropers;"
    cursor = ChurchDBConnection.cursor()
    cursor.execute(sql)

    sql = "CREATE VIEW vwservicewithpropers AS SELECT s.ID as ID,s.ChurchID AS ChurchID,s.DateTime AS DateTime,s.PropersID AS PropersID,p.LiturgicalDate as PropersLiturgicalDate,s.LiturgicalDate AS ServiceLiturgicalDate,s.HolyCommunion AS HolyCommunion,s.OrderofService AS OrderofService,s.OSNote AS OSNote,s.PsalmorIntroit AS PsalmorIntroit,s.SermonID AS SermonID,s.Bulletin AS Bulletin,s.Note AS Note,p.ID AS PID,p.Lectionary AS Lectionary,p.Season AS Season,p.Color AS Color,p.Theme AS Theme,p.Introit AS Introit FROM (tblservice s JOIN tblpropers p ON (s.PropersID = p.ID));"

    cursor = ChurchDBConnection.cursor()
    cursor.execute(sql)

    sql = "DROP VIEW IF EXISTS vwhymnusage;"
    cursor = ChurchDBConnection.cursor()
    cursor.execute(sql)

    sql = "CREATE VIEW vwhymnusage  AS  select u.ID AS ID,s.ID AS ServiceID,s.DateTime AS DateTime,h.ID AS HymnID,h.Hymn AS Hymn,h.Title AS Title,u.UsedAs AS UsedAs,h.BibleText AS BibleText,h.Category AS Category,h.File AS File,u.Note AS Note from ((tblhymnusage u join tblservice s on(u.ServiceID = s.ID)) join tblhymn h on(u.HymnID = h.ID));"
    cursor = ChurchDBConnection.cursor()
    cursor.execute(sql)

    sql = "DROP VIEW IF EXISTS vwserviceroles;"
    cursor = ChurchDBConnection.cursor()
    cursor.execute(sql)

    sql = "CREATE VIEW vwServiceRoles AS SELECT sr.ID as SID, sr.ServiceID, sr.ParticipantID, p.ID as PID, p.Name, sr.Role FROM tblservicerole AS sr, tblparticipant AS p WHERE sr.ParticipantID = p.ID;"
    cursor = ChurchDBConnection.cursor()
    cursor.execute(sql)


parser = argparse.ArgumentParser(
    prog="rptWorshipPlanningWorksheet.py", description="Worship Planning Worksheet"
)
parser.add_argument("--version", action="version", version="%(prog)s 0.1")
parser.add_argument(
    "-I",
    "--ID",
    dest="ID",
    action="store",
    type=int,
    nargs=1,
    help="Enter Service ID",
)
args = parser.parse_args()
if not args.ID:
    print("no Service ID")
    exit()

ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
create_sql_views()

CONFIG.set_Config_DBConnection(ChurchDBConnection)
ReportLocation = CONFIG.get_Config_Value("Location", "Report")


pdf = PDF()

rptService = pdf.load_report_description("rptWorshipPlanning")
rptService["Body"]["Table"]["Service"]["condition"] = rptService["Body"]["Table"][
    "Service"
]["condition"].format(ID=args.ID[0])

pdf.set_auto_page_break(auto=False, margin=rptService["Report"]["PageBreak"])
pdf.setDocumentHeader(**rptService["Header"])
pdf.setDocumentFooter(**rptService["Footer"])
pdf.setDefaultFont(**rptService["Body"]["font"])
pdf.setDefaultBoldFont(**rptService["Body"]["font"])

page_size = 280 - rptService["Header"]["size"] - rptService["Footer"]["size"]
page_left = page_size
#
#   Body of Report
#
pdf.add_page()
pdf.add_font("Arial", "", "c:\\WINDOWS\\FONTS\\arial.ttf", uni=True)

service = clsDB.clsRecord(ChurchDBConnection, rptService["Body"]["Table"]["Service"])
service.load_records(rptService["Body"]["Table"]["Service"])
pdf.print_service(service)

fname = (
    ReportLocation
    #    + rpt_date
    #    + "."
    #    + rpt_time
    #    + "."
    + rptService["Report"]["ReportName"]
)
pdf.output(fname)
subprocess.Popen(
    '"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe" ' + fname, shell=True
)
