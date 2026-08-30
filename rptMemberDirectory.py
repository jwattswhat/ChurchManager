"""Generate the historical PDF member directory outside the visual report path."""

from fpdf import FPDF
from datetime import datetime
import mysql
import mysql.connector
import subprocess
import fnCMargParse
from churchmanager_mode import resolve_database

#   ChurchManager Classes
import JSForm

rpt_fontfamily = 0
rpt_fontstyle = 1
rpt_fontsize = 2
rpt_date = datetime.now().strftime("%d-%b-%Y")
rpt_time = datetime.now().strftime("%H%M")

rptMemberDir = {
    "Report": {"ReportName": "MembershipListing.pdf", "PageBreak": 30.0},
    "Header": {
        "church": "Life in Christ Lutheran Church",
        "titles": ["Membership Directory"],
        "churchfont": {"family": "Arial", "style": "B", "size": 15},
        "titlefont": {"family": "Arial", "style": "B", "size": 13},
        "size": 25,
        "date": rpt_date + " " + rpt_time[:2] + ":" + rpt_time[-2:],
        "linesize": 6,
    },
    "Body": {
        "indent": 0.5,
        "linesize": 6,
        "columnwidth": 500.0,
        "font": {"family": "Arial", "style": "", "size": 15},
        "boldFont": {"family": "Arial", "style": "B", "size": 15},
        "Families": {
            "name": "tblFamily",
            "fields": ["*"],
            "condition": "Directory = True",
            "order by": "FamilyName",
        },
        "FamiliesSQL": "SELECT * FROM tblFamily WHERE Directory = True  ORDER BY FamilyName;",
        "FamilyAddress": {
            "name": "tblFamilyAddress",
            "fields": ["*"],
            "condition": "FamilyID = {FamilyID} and Unlisted=False",
            "order by": "FamilyID",
        },
        "FamilyAddressSQL": "SELECT * FROM tblfamilyAddress WHERE FamilyID={FamilyID} AND Unlisted=False ORDER BY FamilyID;",
        "FamilyContact": {
            "name": "tblFamilyContact",
            "fields": ["*"],
            "condition": "FamilyID = {FamilyID} and Unlisted=False",
            "order by": "FamilyID",
        },
        "FamilyContactSQL": "SELECT * FROM tblfamilyContact WHERE FamilyID={FamilyID} AND Unlisted=False ORDER BY FamilyID;",
        "People": {
            "name": "tblPerson",
            "fields": ["*"],
            "condition": "FamilyID = {FamilyID}",
            "order by": "FamilyID, FirstName",
        },
        "PeopleSQL": "SELECT * FROM tblPerson WHERE FamilyID={FamilyID} ORDER BY FamilyID, FirstName;",
        "PersonAddress": {
            "name": "tblPersonAddress",
            "fields": ["*"],
            "condition": "PersonID = {PersonID} and Unlisted=False",
            "order by": "PersonID",
        },
        "PersonAddressSQL": "SELECT * FROM tblPersonAddress WHERE PersonID={PersonID} AND Unlisted=False ORDER BY PersonID;",
        "PersonContact": {
            "name": "tblPersonContact",
            "fields": ["*"],
            "condition": "PersonID = {PersonID} and Unlisted=False",
            "order by": "PersonID",
        },
        "PersonContactSQL": "SELECT * FROM tblPersonContact WHERE PersonID={PersonID} AND Unlisted=False ORDER BY PersonID;",
    },
    "Footer": {
        "font": {"family": "Arial", "style": "", "size": 10},
        "size": 15.0,
        "linesize": 6,
    },
}


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
                self.cell(0, rptMemberDir["Header"]["linesize"], tl, ln=2, align="C")
        self.cell(
            0, rptMemberDir["Header"]["linesize"], self.REPORTDATE, ln=2, align="R"
        )

    def footer(self):
        self.setFont(**self.FOOTERFONT)
        self.set_y(-self.FOOTERSIZE)
        self.cell(
            0,
            rptMemberDir["Footer"]["linesize"],
            "*Indicates Non-Member",
            ln=0,
            align="L",
        )
        self.cell(
            0, rptMemberDir["Footer"]["linesize"], str(self.page_no()), ln=2, align="C"
        )
        self.ln(20)

    def print_family(self, family):
        familylines = pdf.get_y()
        if family == None:
            return
        self.ic.setstart(10.0, 5.0)
        pdf.print_picture(family)

        # print the family name
        self.set_x(self.ic.val())
        self.setFont(**{"style": "Bold"})
        self.cell(
            rptMemberDir["Body"]["columnwidth"],
            rptMemberDir["Body"]["linesize"],
            txt=family["FamilyName"],
            ln=2,
            border="T",
            align="L",
        )
        self.setFont()

        table = rptMemberDir["Body"]["People"].copy()
        table["condition"] = rptMemberDir["Body"]["People"]["condition"].replace(
            "{FamilyID}", str(family["ID"])
        )
        people = JSForm.clsRecord(ChurchDB.DBConnection, table)
        nr = people.load_records()
        if nr != "NewRecord":
            if people != None:
                self.print_family_member_list(people)

        #   Print all the Family addresses
        #
        table = rptMemberDir["Body"]["FamilyAddress"].copy()
        table["condition"] = rptMemberDir["Body"]["FamilyAddress"]["condition"].replace(
            "{FamilyID}", str(family["ID"])
        )
        addresses = JSForm.clsRecord(ChurchDB.DBConnection, table)
        nr = addresses.load_records()
        if nr != "NewRecord":
            address = addresses.first()
            while address != None:
                self.print_address(address)
                address = addresses.next()

        #
        #   Print all the Family Contacts
        table = rptMemberDir["Body"]["FamilyContact"].copy()
        table["condition"] = rptMemberDir["Body"]["FamilyContact"]["condition"].replace(
            "{FamilyID}", str(family["ID"])
        )
        contacts = JSForm.clsRecord(ChurchDB.DBConnection, table)
        nr = contacts.load_records()
        if nr != "NewRecord":
            contact = contacts.first()
            while contact != None:
                self.print_contact(contact)
                contact = contacts.next()
        #
        #   Print all the Person addresses and contact
        #
        person = people.first()
        while person != None:
            if person["Member"] == True:
                self.member_count += 1
            pdf.print_person(person)
            person = people.next()

        while (familylines + 43) > pdf.get_y():
            pdf.ln()

    def print_picture(self, family):
        if family == None:
            return

        # force pdf to check for page overflow
        if self.get_y() + 43 > 279.0 - rptMemberDir["Footer"]["size"]:
            self.add_page()
        if family["Picture"] == None:
            self.image(DefaultPicture, x=150, y=self.get_y() + 3, h=40)
        else:
            self.image(
                PictureLocation + family["Picture"], x=150, y=self.get_y() + 3, h=40
            )

    def print_family_member_list(self, people):
        if people == None:
            return
        """ 
            print_person_list : print a list of people in the specified family
        """
        person = people.first()
        line = ""
        while person != None:
            if line == "":
                line = person["FirstName"]
            else:
                line = ", ".join([line, person["FirstName"]])
            if person["Member"] == False:
                line += "*"
            person = people.next()
        self.setFont(**{"style": "Bold"})
        self.set_x(self.ic.inn())
        self.cell(
            rptMemberDir["Body"]["columnwidth"],
            rptMemberDir["Body"]["linesize"],
            txt=line,
            ln=2,
            align="L",
        )
        self.set_x(self.ic.out())
        self.setFont()

    def print_address(self, address):
        if address == None:
            return
        self.set_x(self.ic.inn())
        self.cell(
            rptMemberDir["Body"]["columnwidth"],
            rptMemberDir["Body"]["linesize"],
            txt=address["AddressLabel"],
            ln=2,
            align="L",
        )
        self.set_x(self.ic.inn())
        if address["Address"] != None:
            self.cell(
                rptMemberDir["Body"]["columnwidth"],
                5,
                txt=address["Address"],
                ln=2,
                align="L",
            )
        if address["Address2"] != None:
            self.cell(
                rptMemberDir["Body"]["columnwidth"],
                rptMemberDir["Body"]["linesize"],
                txt=address["Address2"],
                ln=2,
                align="L",
            )
        city = address["City"]
        if city == None:
            city = ""
        state = address["State"]
        if state == None:
            state = ""
        zipcode = address["Zip"]
        if zipcode == None:
            zipcode = ""
        self.cell(
            rptMemberDir["Body"]["columnwidth"],
            rptMemberDir["Body"]["linesize"],
            txt=city + ", " + state + " " + zipcode,
            ln=2,
            align="L",
        )
        self.set_x(self.ic.out())
        self.set_x(self.ic.out())

    def print_contact(self, contact):
        if contact == None:
            return

        line = (
            contact["ContactLabel"]
            + " : "
            + contact["Type"]
            + " : "
            + contact["Contact"]
        )
        self.set_x(self.ic.inn())
        self.multi_cell(
            rptMemberDir["Body"]["columnwidth"],
            rptMemberDir["Body"]["linesize"],
            txt=line,
            align="L",
        )
        self.set_x(self.ic.out())

    def get_member_count(self):
        return self.member_count

    def print_member_count(self):
        self.set_y(self.get_y() + 45)
        self.cell(
            0,
            rptMemberDir["Body"]["linesize"],
            txt="Member Count: " + str(self.member_count),
            ln=2,
            align="C",
        )

    def print_person(self, person):
        if person == None:
            return
        #   Print the name
        self.ln(1)
        self.set_x(self.ic.inn())
        self.setFont(**{"style": "Bold"})
        self.cell(
            rptMemberDir["Body"]["columnwidth"],
            rptMemberDir["Body"]["linesize"],
            txt=person["FirstName"],
            ln=2,
            align="L",
        )
        self.setFont()

        #   Read the Person Addresses
        table = rptMemberDir["Body"]["PersonAddress"].copy()
        table["condition"] = rptMemberDir["Body"]["PersonAddress"]["condition"].replace(
            "{PersonID}", str(person["ID"])
        )
        addresses = JSForm.clsRecord(ChurchDB.DBConnection, table)
        #   Print the addresses
        nr = addresses.load_records()
        if nr != "NewRecord":
            address = addresses.first()
            while address != None:
                self.print_address(address)
                address = addresses.next()

        #   Print the Person Contacts
        table = rptMemberDir["Body"]["PersonContact"].copy()
        table["condition"] = rptMemberDir["Body"]["PersonContact"]["condition"].replace(
            "{PersonID}", str(person["ID"])
        )
        contacts = JSForm.clsRecord(ChurchDB.DBConnection, table)
        nr = contacts.load_records()
        if nr != "NewRecord":
            contact = contacts.first()
            while contact != None:
                self.print_contact(contact)
                contact = contacts.next()

        self.set_x(self.ic.out())


arguments = fnCMargParse.CMargs(
    "rptMemberDirectory", "Member Directory",
    ["server", "database", "user", "test_mode"],
)
arguments = resolve_database(arguments, resolve_credentials=False)
ChurchDB = JSForm.clsDB(
    arguments["server"], arguments["database"], arguments["user"], None,
    credential_target=arguments["credential_target"],
)
JSForm.CONFIG.set_Config_DBConnection(ChurchDB.DBConnection)
PictureLocation = JSForm.CONFIG.get_Config_Value("Location", "Picture")
DefaultPicture = PictureLocation + "Default.jpg"
ReportLocation = JSForm.CONFIG.get_Config_Value("Location", "Report")

pdf = PDF()
pdf.set_auto_page_break(auto=False, margin=rptMemberDir["Report"]["PageBreak"])
pdf.setDocumentHeader(**rptMemberDir["Header"])
pdf.setDocumentFooter(**rptMemberDir["Footer"])
pdf.setDefaultFont(**rptMemberDir["Body"]["font"])
pdf.setDefaultBoldFont(**rptMemberDir["Body"]["font"])

page_size = 280 - rptMemberDir["Header"]["size"] - rptMemberDir["Footer"]["size"]
page_left = page_size
#
#   Body of Report
#
pdf.add_page()
pdf.setFont()

families = JSForm.clsRecord(ChurchDB.DBConnection, rptMemberDir["Body"]["Families"])
families.load_records()
family = families.first()
while family != None:
    pdf.print_family(family)
    family = families.next()
    page_left = page_size - pdf.get_y()
    if page_left <= 20:
        pdf.add_page()
        page_left = page_size
pdf.print_member_count()

fname = ReportLocation + rptMemberDir["Report"]["ReportName"]

# + rpt_date
# + "."
# + rpt_time
# + "."
pdf.output(fname)

os.startfile(fname)
