"""Official non-accounting visual-report inventory and secure tabular contracts."""

from dataclasses import dataclass
from pathlib import Path


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
    dataset_version: int = 1
    row_color_field: str | None = None
    filter_fields: tuple[str, ...] = ()


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
    ReportSpec("CMRP01", "Available Reports Listing", "reports.general.run", "rpt_report_catalog", (
        c("Report", "Code", 75), c("Title", "Report", 225), c("Params", "Parameters", 160),
        c("Note", "Notes", 155)), "Title", 1, "landscape"),

    ReportSpec("CMAT01", "Attendance - Event Listing", "reports.attendance.run", "rpt_attendance_event", (
        c("DateTime", "Date and Time", 95, "datetime"), c("Description", "Event", 155),
        c("AttendanceType", "Type", 80), c("HandCount", "Total", 55, "integer", "right"),
        c("KnownAttendance", "Known", 55, "integer", "right"),
        c("UnnamedAttendance", "Unnamed", 60, "integer", "right"),
        c("HandCountCommunion", "Communion", 65, "integer", "right")),
        "DateTime DESC", 2, "landscape", 2),
    ReportSpec("CMAT02", "Attendance - Weekly Summary", "reports.attendance.run", "rpt_attendance_weekly", (
        c("DateTime", "Week beginning", 105, "date"), c("AttendanceType", "Type", 120),
        c("EventCount", "Events", 60, "integer", "right"),
        c("Attendance", "Total", 70, "integer", "right"),
        c("KnownAttendance", "Known", 70, "integer", "right"),
        c("UnnamedAttendance", "Unnamed", 75, "integer", "right"),
        c("Communion", "Communion", 75, "integer", "right")),
        "DateTime DESC, AttendanceType", 2, dataset_version=2),
    ReportSpec("CMAT03", "Attendance - Individual History", "reports.attendance.run", "rpt_individual_attendance", (
        c("DateTime", "Date and Time", 100, "datetime"), c("LastName", "Last Name", 95),
        c("FirstName", "First Name", 90), c("Description", "Event", 145),
        c("AttendanceType", "Type", 90), c("Communion", "Communion", 70, "boolean"),
        c("Note", "Note", 130)), "LastName, FirstName, DateTime DESC", 2, "landscape",
        filter_fields=("PersonID",)),
    ReportSpec("CMAT04", "Attendance - Pastor's Comparison", "reports.attendance.run", "rpt_pastors_attendance_comparison", (
        c("ReportYear", "Year", 65, "integer"),
        c("FullYearAttendance", "Full-year total", 100, "integer", "right"),
        c("ThroughDateAttendance", "Total through today", 115, "integer", "right"),
        c("EventsThroughDate", "Events", 70, "integer", "right"),
        c("AverageThroughDate", "Average", 80, "decimal", "right"),
        c("CommunionThroughDate", "Communion", 90, "integer", "right")),
        "ReportYear DESC", 2),
    ReportSpec("CMAT05", "Attendance - Member Follow-up", "reports.attendance.run", "rpt_member_attendance_followup", (
        c("LastName", "Last Name", 120), c("FirstName", "First Name", 110),
        c("LastAttended", "Last attended", 100, "date"),
        c("MissedWeeks", "Consecutive weeks missed", 130, "integer", "right"),
        c("Status", "Member status", 100)), "MissedWeeks DESC, LastName, FirstName", 2,
        row_color_field="FlagColor"),
    ReportSpec("CMHU01", "Hymn Usage by Service", "reports.worship.run", "rpt_hymn_usage", (
        c("ServiceID", "Service", 75, "integer"), c("UsedAs", "Used As", 110),
        c("HymnID", "Hymn ID", 75, "integer"), c("Note", "Notes", 275)), "ServiceID DESC, UsedAs", 2),
    ReportSpec("CMHU02", "Hymn Usage by Hymn", "reports.worship.run", "rpt_hymn", (
        c("Hymn", "Hymn", 60), c("Title", "Title", 175), c("Tune", "Tune", 145),
        c("Category", "Category", 95), c("BibleText", "Bible Text", 85)), "Hymn", 2),
    ReportSpec("CMHU03", "Selected Hymn Usage", "reports.worship.run", "rpt_hymn_usage", (
        c("HymnID", "Hymn ID", 70, "integer"), c("ServiceID", "Service", 75, "integer"),
        c("UsedAs", "Used As", 120), c("Note", "Notes", 275)), "ServiceID DESC", 2),
    ReportSpec("CMHU04", "Recent Hymn Usage", "reports.worship.run", "rpt_hymn_usage", (
        c("ServiceID", "Service", 75, "integer"), c("HymnID", "Hymn ID", 70, "integer"),
        c("UsedAs", "Used As", 120), c("Note", "Notes", 275)), "ServiceID DESC", 2),
    ReportSpec("CMHU05", "Favorite Hymns", "reports.worship.run", "rpt_favorite_hymn", (
        c("PrintedReference", "Hymn", 80), c("Title", "Title", 190),
        c("Tune", "Tune", 145), c("Category", "Category", 100),
        c("BibleText", "Scripture", 95)), "PrintedReference, Title", 2,
        filter_fields=("HymnalID",)),
    ReportSpec("CMWS01", "Worship Services by Date", "reports.worship.run", "rpt_service", (
        c("DateTime", "Date and Time", 100, "datetime"), c("LiturgicalDate", "Liturgical Day", 150),
        c("Location", "Location", 95), c("OrderofService", "Service", 110),
        c("Attendance", "Attendance", 65, "integer", "right")), "DateTime DESC", 2),

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
    ReportSpec("CMWP01", "Worship Service Planner", "reports.worship.run", "rpt_service", (
        c("DateTime", "Date and Time", 100, "datetime"), c("LiturgicalDate", "Liturgical Day", 160),
        c("Location", "Location", 120), c("OrderofService", "Order of Service", 185)),
        "DateTime DESC", 4),

    ReportSpec("CMGR01", "Groups - Current Roster", "groups.reports.view", "rpt_group_current_roster", (
        c("GroupName", "Group", 145), c("LastName", "Last Name", 115),
        c("FirstName", "First Name", 105), c("Roles", "Role(s)", 105),
        c("StartDate", "Member Since", 70, "date")),
        "LastName, FirstName", 4, filter_fields=("GroupID",)),
    ReportSpec("CMGR02", "Groups - Person Participation History", "groups.reports.view", "rpt_person_group_participation", (
        c("LastName", "Last Name", 95), c("FirstName", "First Name", 90),
        c("GroupName", "Group", 140), c("MembershipStatus", "Status", 65),
        c("StartDate", "Started", 70, "date"), c("EndDate", "Ended", 70, "date")),
        "LastName, FirstName, StartDate DESC", 4, filter_fields=("PersonID",)),
    ReportSpec("CMGR03", "Groups - Meeting Attendance", "groups.reports.view", "rpt_group_meeting_attendance", (
        c("StartsAt", "Date and Time", 95, "datetime"), c("MeetingTitle", "Meeting", 130),
        c("LastName", "Last Name", 100), c("FirstName", "First Name", 95),
        c("AttendanceStatus", "Attendance", 75), c("MeetingStatus", "Meeting Status", 85)),
        "StartsAt DESC, LastName, FirstName", 4, "landscape", filter_fields=("GroupID",)),
    ReportSpec("CMGR04", "Groups - Attendance Sheet", "groups.reports.view", "rpt_group_attendance_sheet", (
        c("LastName", "Last Name", 92), c("FirstName", "First Name", 82),
        c("Roles", "Role(s)", 86), c("Present", "Present", 48),
        c("Absent", "Absent", 46), c("Excused", "Excused", 50),
        c("Notes", "Notes", 136)),
        "LastName, FirstName", 4, "landscape",
        filter_fields=("GroupID", "MembershipStartDate", "MembershipEndDate")),

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
    ReportSpec("CMPC01", "Pastoral Care - Work List", "pastoral.care.report", "rpt_pastoral_care_work_list", (
        c("Subject", "Subject", 150), c("Category", "Category", 105),
        c("Assignee", "Assigned To", 120), c("Priority", "Priority", 65),
        c("Status", "Status", 70), c("DueDate", "Due", 75, "date"),
        c("NextFollowUpDate", "Next Follow-up", 90, "date"),
        c("ScheduleText", "Schedule", 145)), "DueDate, Priority DESC, Subject", 6, "landscape"),
    ReportSpec("CMPC02", "Pastoral Care - Activity Summary", "pastoral.care.report", "rpt_pastoral_care_activity_summary", (
        c("ActionDate", "Date", 85, "date"), c("Category", "Category", 150),
        c("ActionType", "Action", 110), c("Result", "Result", 110),
        c("ActionCount", "Count", 75, "integer", "right")),
        "ActionDate DESC, Category, ActionType, Result", 6),
)


REPORTS_BY_CODE = {spec.code: spec for spec in SPECS}
_DEFINITION_CODES = frozenset(
    path.stem for path in (Path(__file__).resolve().parent / "definitions").glob("*.json")
)
OFFICIAL_CODES = frozenset(REPORTS_BY_CODE) | _DEFINITION_CODES
CONSOLIDATED_CODES = frozenset({"CMAD01", "CMPH01"})
DISABLED_CODES = frozenset({"CMSM01"})
LAUNCHER_CODES = frozenset({"CMBATCH00"})
RETIRED_CODES = CONSOLIDATED_CODES | DISABLED_CODES | LAUNCHER_CODES | frozenset({
    "CMFD01", "CMCL01", "CMDN01", "CMDN02", "CFCA01", "CFCR01", "CFGR01",
})
