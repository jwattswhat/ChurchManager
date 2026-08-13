"""Secure single-service dataset for the Worship Planning Worksheet."""

from JSForm.report_dataset import (
    ReportCollection, ReportDataset, ReportDatasetContract, ReportField,
)


WORSHIP_PLANNING_CONTRACT = ReportDatasetContract(
    "churchmanager.cmwp01", 3, "reports.worship.run",
    (
        ReportCollection("church", "Church", (
            ReportField("ID", "Church ID", "integer"),
            ReportField("Church", "Church Name"),
            ReportField("Logo", "Church Logo", "image"),
        )),
        ReportCollection("parameters", "Parameters", (
            ReportField("Display", "Selected Parameters"),
        )),
        ReportCollection("service", "Worship Service", (
            ReportField("ID", "Service ID", "integer"),
            ReportField("DateTime", "Date and Time", "datetime"),
            ReportField("Location", "Location"),
            ReportField("LiturgicalDate", "Liturgical Date"),
            ReportField("HolyCommunion", "Holy Communion", "boolean"),
            ReportField("Lectionary", "Lectionary"),
            ReportField("Season", "Season"),
            ReportField("Color", "Color"),
            ReportField("Theme", "Theme"),
            ReportField("OrderOfService", "Order of Service"),
            ReportField("Sermon", "Sermon"),
            ReportField("Bulletin", "Bulletin"),
            ReportField("OSNote", "Order of Service Note"),
            ReportField("Note", "Service Note"),
        )),
        ReportCollection("order_lines", "Order of Service", (
            ReportField("Sequence", "Sequence", "integer"),
            ReportField("Label", "Order of Service"),
            ReportField("Detail", "Selection or Reference"),
        )),
        ReportCollection("readings", "Readings", (
            ReportField("Reading", "Reading"), ReportField("Reference", "Reference"),
        )),
        ReportCollection("hymns", "Selected Hymns", (
            ReportField("UsedAs", "Use"), ReportField("Hymn", "Hymn"),
        )),
        ReportCollection("participants", "Participants", (
            ReportField("Role", "Role"), ReportField("Name", "Participant"),
            ReportField("Status", "Status"),
        )),
    ),
)


class WorshipPlanningDatasetProvider:
    """Build the planner exclusively from the approved worship report views."""

    def __init__(self, connection, authorization):
        self.connection = connection
        self.authorization = authorization
        self.marker = "%s" if "mysql.connector" in type(connection).__module__ else "?"

    def _rows(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql.replace("?", self.marker), values)
            columns = tuple(item[0] for item in cursor.description)
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    @staticmethod
    def _placeholder(rows, **values):
        return rows or [values]

    @staticmethod
    def _participant_plan(requirements, assignments):
        """Show every required slot plus any additional or declined assignment."""
        remaining = list(assignments)
        result = []
        for requirement in requirements:
            role_id = requirement["WorshipRoleID"]
            role = requirement["Role"]
            required = int(requirement["RequiredCount"])
            available = [
                row for row in remaining
                if row["WorshipRoleID"] == role_id and row["Status"] != "DECLINED"
            ]
            for slot in range(1, required + 1):
                position = f"{role} {slot}" if required > 1 else role
                assignment = available.pop(0) if available else None
                if assignment:
                    remaining.remove(assignment)
                    result.append({
                        "Role": position, "Name": assignment["Name"],
                        "Status": str(assignment["Status"]).title(),
                    })
                else:
                    result.append({"Role": position, "Name": "Unfilled", "Status": "Open"})
        for assignment in remaining:
            result.append({
                "Role": assignment["Role"], "Name": assignment["Name"],
                "Status": str(assignment["Status"]).title(),
            })
        return result

    def build(self, church_id, service_id):
        self.authorization.require(
            WORSHIP_PLANNING_CONTRACT.required_permission,
            operation="Create Worship Planning Worksheet dataset",
        )
        if service_id in (None, "", "All"):
            raise ValueError("Select a Worship Service before running the planning worksheet.")

        church = self._rows(
            "SELECT ID,Church,Logo FROM rpt_church_identity WHERE ID=?", (church_id,),
        )
        service = self._rows(
            "SELECT ID,DateTime,Location,LiturgicalDate,HolyCommunion,Lectionary,"
            "Season,Color,Theme,OrderOfService,Sermon,Bulletin,OSNote,Note "
            "FROM rpt_worship_planner_service WHERE ChurchID=? AND ID=?",
            (church_id, service_id),
        )
        if not service:
            raise ValueError("The selected Worship Service is unavailable.")

        order_lines = self._rows(
            "SELECT Sequence,Label,TRIM(CONCAT_WS('  ',NULLIF(WeeklyValue,''),"
            "NULLIF(ReferenceText,''))) AS Detail FROM rpt_worship_planner_order "
            "WHERE ServiceID=? ORDER BY Sequence,ID", (service_id,),
        )
        readings = self._rows(
            "SELECT Reading,Reference FROM rpt_worship_planner_reading "
            "WHERE ServiceID=? ORDER BY SortOrder,ID", (service_id,),
        )
        hymns = self._rows(
            "SELECT UsedAs,Hymn FROM rpt_worship_planner_hymn "
            "WHERE ServiceID=? ORDER BY Sequence,ID", (service_id,),
        )
        requirements = self._rows(
            "SELECT WorshipRoleID,Role,RequiredCount "
            "FROM rpt_worship_planner_required_position WHERE ServiceID=? ORDER BY Role",
            (service_id,),
        )
        assignments = self._rows(
            "SELECT WorshipRoleID,Role,Name,Status FROM rpt_worship_planner_participant "
            "WHERE ServiceID=? ORDER BY Role,Name", (service_id,),
        )
        participants = self._participant_plan(requirements, assignments)
        label = service[0]["LiturgicalDate"] or str(service[0]["DateTime"])
        return ReportDataset.create(WORSHIP_PLANNING_CONTRACT, {
            "church": church,
            "parameters": [{"Display": label}],
            "service": service,
            "order_lines": self._placeholder(
                order_lines, Sequence=0, Label="No weekly order of service has been saved.", Detail="",
            ),
            "readings": self._placeholder(readings, Reading="Readings", Reference="Not selected"),
            "hymns": self._placeholder(hymns, UsedAs="Hymns", Hymn="Not selected"),
            "participants": self._placeholder(
                participants, Role="Participants", Name="Not assigned", Status="Open",
            ),
        })
