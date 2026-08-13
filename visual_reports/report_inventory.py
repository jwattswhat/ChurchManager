"""Official non-accounting visual-report inventory and secure tabular contracts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Column:
    field: str
    label: str
    width: int
    data_type: str = "text"
    align: str = "left"


@dataclass(frozen=True)
class ReportSpec:
    code: str
    title: str
    permission: str
    view: str
    columns: tuple[Column, ...]
    order_by: str
    wave: int
    orientation: str = "portrait"


def c(field, label, width, data_type="text", align="left"):
    return Column(field, label, width, data_type, align)


SPECS = (
    ReportSpec("CMAS01", "Asset Listing", "reports.general.run", "rpt_asset", (
        c("AssetID", "Asset", 85), c("Description", "Description", 220),
        c("PurchaseDate", "Purchased", 80, "date"), c("Reserve", "Reserve", 75, "currency", "right"),
        c("Depreciate", "Depreciate", 70, "boolean")), "AssetID", 1),
    ReportSpec("CMDO01", "Document Listing", "reports.general.run", "rpt_document", (
        c("DocumentType", "Type", 85), c("Date", "Date", 75, "date"),
        c("Title", "Title", 170), c("Document", "Document", 210)), "DocumentType, Date DESC, Title", 1),
    ReportSpec("CMEN01", "Enhancement and Bug List", "reports.general.run", "rpt_enhancement", (
        c("Priority", "Priority", 55), c("Module", "Module", 80), c("Screen", "Screen", 80),
        c("Description", "Description", 235), c("DateDue", "Due", 70, "date"),
        c("Complete", "Done", 45, "boolean")), "Complete, Priority, DateDue", 1, "landscape"),
    ReportSpec("CMRP01", "Available Reports Listing", "reports.general.run", "rpt_report_catalog", (
        c("Report", "Code", 75), c("Title", "Report", 225), c("Params", "Parameters", 160),
        c("Note", "Notes", 155)), "Title", 1, "landscape"),

    ReportSpec("CMAT01", "Attendance Event Listing", "reports.attendance.run", "rpt_attendance_event", (
        c("DateTime", "Date and Time", 100, "datetime"), c("Description", "Event", 175),
        c("AttendanceType", "Type", 90), c("HandCount", "Attendance", 70, "integer", "right"),
        c("HandCountCommunion", "Communion", 70, "integer", "right")), "DateTime DESC", 2),
    ReportSpec("CMAT02", "Weekly Attendance Listing", "reports.attendance.run", "rpt_attendance_event", (
        c("DateTime", "Week / Service", 110, "datetime"), c("Description", "Event", 190),
        c("AttendanceType", "Type", 100), c("HandCount", "Attendance", 70, "integer", "right"),
        c("HandCountCommunion", "Communion", 70, "integer", "right")), "DateTime DESC", 2),
    ReportSpec("CMHU01", "Hymn Usage by Service", "reports.worship.run", "rpt_hymn_usage", (
        c("ServiceID", "Service", 75, "integer"), c("UsedAs", "Used As", 110),
        c("HymnID", "Hymn ID", 75, "integer"), c("Note", "Notes", 275)), "ServiceID DESC, UsedAs", 2),
    ReportSpec("CMHU02", "Hymn Usage by Hymn", "reports.worship.run", "rpt_hymn", (
        c("Hymn", "Hymn", 65), c("Title", "Title", 210), c("Category", "Category", 130),
        c("BibleText", "Bible Text", 125)), "Hymn", 2),
    ReportSpec("CMHU03", "Selected Hymn Usage", "reports.worship.run", "rpt_hymn_usage", (
        c("HymnID", "Hymn ID", 70, "integer"), c("ServiceID", "Service", 75, "integer"),
        c("UsedAs", "Used As", 120), c("Note", "Notes", 275)), "ServiceID DESC", 2),
    ReportSpec("CMHU04", "Recent Hymn Usage", "reports.worship.run", "rpt_hymn_usage", (
        c("ServiceID", "Service", 75, "integer"), c("HymnID", "Hymn ID", 70, "integer"),
        c("UsedAs", "Used As", 120), c("Note", "Notes", 275)), "ServiceID DESC", 2),
    ReportSpec("CMWS01", "Worship Services by Date", "reports.worship.run", "rpt_service", (
        c("DateTime", "Date and Time", 100, "datetime"), c("LiturgicalDate", "Liturgical Day", 150),
        c("Location", "Location", 95), c("OrderofService", "Service", 110),
        c("Attendance", "Attendance", 65, "integer", "right")), "DateTime DESC", 2),

    ReportSpec("CMPJ01", "Projects", "reports.ministry.run", "rpt_project", (
        c("Priority", "Priority", 55), c("Project", "Project", 150), c("Description", "Description", 230),
        c("StartDate", "Start", 70, "date"), c("EndDate", "End", 70, "date"),
        c("Complete", "Done", 45, "boolean")), "Priority, Project", 3, "landscape"),
    ReportSpec("CMPJ02", "Incomplete Projects", "reports.ministry.run", "rpt_project", (
        c("Priority", "Priority", 55), c("Project", "Project", 160), c("Description", "Description", 250),
        c("AssignedToText", "Assigned To", 105), c("EndDate", "Due", 70, "date")), "Priority, EndDate", 3, "landscape"),
    ReportSpec("CMPJ03", "Project Sign Up Sheet", "reports.ministry.run", "rpt_project", (
        c("Project", "Project", 150), c("Description", "Description", 250),
        c("StartDate", "Starts", 75, "date"), c("EndDate", "Ends", 75, "date"),
        c("AssignedToText", "Volunteer", 100)), "Project", 3, "landscape"),
    ReportSpec("CMPJ04", "Project Task Listing", "reports.ministry.run", "rpt_task", (
        c("Priority", "Priority", 55), c("ProjectID", "Project", 65, "integer"), c("Task", "Task", 150),
        c("Description", "Description", 240), c("EndDate", "Due", 70, "date"),
        c("Complete", "Done", 45, "boolean")), "ProjectID, Priority, Task", 3, "landscape"),

    ReportSpec("CMMI01", "Member Information", "reports.membership.contact", "rpt_membership_person", (
        c("LastName", "Last Name", 105), c("FirstName", "First Name", 95), c("Status", "Status", 85),
        c("MaritalStatus", "Marital Status", 90), c("Member", "Member", 60, "boolean"),
        c("AssociateMember", "Associate", 65, "boolean")), "LastName, FirstName", 4),
    ReportSpec("CMMI02", "Member Information Listing", "reports.membership.contact", "rpt_membership_person", (
        c("LastName", "Last Name", 105), c("FirstName", "First Name", 95), c("Status", "Status", 85),
        c("MaritalStatus", "Marital Status", 90), c("Member", "Member", 60, "boolean"),
        c("Voter", "Voter", 60, "boolean")), "LastName, FirstName", 4),
    ReportSpec("CMMI03", "Member Update Forms", "reports.membership.contact", "rpt_membership_person", (
        c("LastName", "Last Name", 105), c("FirstName", "First Name", 95), c("Status", "Status", 85),
        c("MaritalStatus", "Marital Status", 90), c("Baptized", "Baptized", 65, "boolean"),
        c("Confirmed", "Confirmed", 65, "boolean")), "LastName, FirstName", 4),
    ReportSpec("CMML01", "Member Status List", "reports.membership.run", "rpt_membership_person", (
        c("Status", "Status", 95), c("LastName", "Last Name", 125), c("FirstName", "First Name", 115),
        c("Member", "Member", 65, "boolean"), c("AssociateMember", "Associate", 75, "boolean"),
        c("Voter", "Voter", 60, "boolean")), "Status, LastName, FirstName", 4),
    ReportSpec("CMML02", "Member Date Listing", "reports.membership.run", "rpt_person_date", (
        c("DateType", "Date Type", 120), c("Date", "Date", 90, "date"),
        c("PersonID", "Person ID", 75, "integer"), c("Note", "Notes", 250)), "DateType, Date DESC", 4),
    ReportSpec("CMPE01", "Membership Transfers", "reports.membership.run", "rpt_person_date", (
        c("Date", "Date", 90, "date"), c("DateType", "Transfer Type", 130),
        c("PersonID", "Person ID", 75, "integer"), c("Note", "Notes", 235)), "Date DESC", 4),
    ReportSpec("CMPH02", "Member Contact Listing", "reports.membership.contact", "rpt_person_contact", (
        c("PersonID", "Person ID", 75, "integer"), c("ContactLabel", "Label", 100),
        c("Type", "Type", 90), c("Contact", "Contact", 275)), "PersonID, Type, ContactLabel", 4),
    ReportSpec("CMWP01", "Worship Planning Worksheet", "reports.worship.run", "rpt_service", (
        c("DateTime", "Date and Time", 100, "datetime"), c("LiturgicalDate", "Liturgical Day", 160),
        c("Location", "Location", 120), c("OrderofService", "Order of Service", 185)),
        "DateTime DESC", 4),

    ReportSpec("CMJR01", "Journal", "reports.pastoral.confidential", "rpt_journal", (
        c("StartDate", "Start", 75, "date"), c("EndDate", "End", 75, "date"), c("Event", "Event", 180),
        c("Complete", "Complete", 65, "boolean"), c("Note", "Notes", 245)), "StartDate DESC", 5, "landscape"),
    ReportSpec("CMPA01", "Pastor's Report", "reports.pastoral.confidential", "rpt_pastor_report", (
        c("Date", "Date", 90, "date"), c("Pastor", "Pastor", 140), c("Reported", "Reported", 80, "boolean"),
        c("Note", "Notes", 300)), "Date DESC", 5),
    ReportSpec("CMPR01", "Prayer Requests", "reports.pastoral.confidential", "rpt_journal", (
        c("StartDate", "Date", 80, "date"), c("Event", "Request", 190),
        c("Complete", "Complete", 65, "boolean"), c("EndDate", "Ended", 80, "date"),
        c("Note", "Pastoral Notes", 225)), "Complete, StartDate DESC", 5, "landscape"),
)


REPORTS_BY_CODE = {spec.code: spec for spec in SPECS}
OFFICIAL_CODES = frozenset(REPORTS_BY_CODE) | {"CMMD01"}
CONSOLIDATED_CODES = frozenset({"CMAD01", "CMPH01"})
DISABLED_CODES = frozenset({"CMSM01"})
LAUNCHER_CODES = frozenset({"CMBATCH00"})
