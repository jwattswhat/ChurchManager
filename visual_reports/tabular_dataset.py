"""Secure dataset provider for standardized ChurchManager tabular reports."""

from JSForm.report_dataset import ReportCollection, ReportDataset, ReportDatasetContract, ReportField

from visual_reports.report_inventory import REPORTS_BY_CODE


CHURCH_FIELDS = (
    ReportField("ID", "Church ID", "integer"), ReportField("Church", "Church Name"),
    ReportField("Logo", "Church Logo", "image"),
)


def contract_for(code):
    spec = REPORTS_BY_CODE[code]
    record_fields = [
        ReportField(column.field, column.label, column.data_type)
        for column in spec.columns
    ]
    if spec.row_color_field:
        record_fields.append(ReportField(spec.row_color_field, "Row color"))
    return ReportDatasetContract(
        f"churchmanager.{code.lower()}", spec.dataset_version, spec.permission,
        (
            ReportCollection("church", "Church", CHURCH_FIELDS),
            ReportCollection("parameters", "Parameters", (ReportField("Display", "Selected Parameters"),)),
            ReportCollection("records", spec.title, tuple(record_fields)),
        ),
    )


class TabularDatasetProvider:
    """Reads only the allowlisted safe view declared by an official report spec."""

    def __init__(self, connection, authorization):
        self.connection = connection
        self.authorization = authorization
        self.marker = "%s" if "mysql.connector" in type(connection).__module__ else "?"

    def build(self, code, church_id, parameters=None):
        spec = REPORTS_BY_CODE[code]
        contract = contract_for(code)
        self.authorization.require(spec.permission, operation=f"Create {code} report dataset")
        parameters = dict(parameters or {})
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"SELECT ID,Church,Logo FROM rpt_church_identity WHERE ID={self.marker}",
                (church_id,),
            )
            church = self._rows(cursor)
            source, where, values = self._scope(spec.view, church_id)
            prefix = "r." if " JOIN " in source else ""
            fields = ",".join(prefix + column.field for column in spec.columns)
            filters, filter_values = self._parameter_filters(spec, parameters)
            if filters:
                where.extend(filters)
                values.extend(filter_values)
            sql = f"SELECT {fields} FROM {source}"
            if where:
                sql += " WHERE " + " AND ".join(where)
            order_by = ", ".join(prefix + part.strip() for part in spec.order_by.split(","))
            sql += f" ORDER BY {order_by}"
            cursor.execute(sql, tuple(values))
            records = self._rows(cursor)
            if spec.row_color_field:
                threshold = self._positive_integer(parameters.get("MissedWeeks"), 3)
                for record in records:
                    record[spec.row_color_field] = (
                        "#C00000" if int(record.get("MissedWeeks") or 0) >= threshold
                        else "#000000"
                    )
        finally:
            cursor.close()
        display = "; ".join(
            f"{key}: {value}" for key, value in parameters.items()
            if value not in (None, "", "All")
        ) or "All records"
        return ReportDataset.create(contract, {
            "church": church, "parameters": [{"Display": display}], "records": records,
        })

    def _scope(self, view, church_id):
        marker = self.marker
        direct = {
            "rpt_asset", "rpt_document", "rpt_attendance_event", "rpt_attendance_weekly",
            "rpt_individual_attendance", "rpt_pastors_attendance_comparison",
            "rpt_member_attendance_followup", "rpt_service",
            "rpt_membership_person", "rpt_directory_family",
            "rpt_journal", "rpt_pastor_report",
        }
        if view in direct:
            return view, [f"ChurchID={marker}"], [church_id]
        if view == "rpt_hymn_usage":
            return "rpt_hymn_usage r JOIN rpt_service s ON s.ID=r.ServiceID", [f"s.ChurchID={marker}"], [church_id]
        if view in {"rpt_person_date", "rpt_person_contact"}:
            return f"{view} r JOIN rpt_membership_person p ON p.ID=r.PersonID", [f"p.ChurchID={marker}"], [church_id]
        if view in {"rpt_report_catalog", "rpt_hymn", "rpt_favorite_hymn"}:
            return view, [], []
        raise ValueError(f"Report view is not approved: {view}")

    def _parameter_filters(self, spec, parameters):
        field_names = {column.field for column in spec.columns} | set(spec.filter_fields)
        filters, values = [], []
        for parameter, field in (
            ("PersonID", "PersonID"), ("HymnID", "HymnID"),
            ("HymnalID", "HymnalID"),
            ("ServiceID", "ServiceID"),
        ):
            value = parameters.get(parameter)
            if value not in (None, "", "All") and field in field_names:
                filters.append(f"{field}={self.marker}")
                values.append(value)
        date_field = next((name for name in ("DateTime", "Date", "StartDate") if name in field_names), None)
        if date_field and parameters.get("StartDate"):
            filters.append(f"{date_field}>={self.marker}")
            values.append(parameters["StartDate"])
        if date_field and parameters.get("EndDate"):
            filters.append(f"{date_field}<={self.marker}")
            values.append(parameters["EndDate"])
        if "AttendanceType" in field_names and parameters.get("AttendanceType") not in (None, "", "All"):
            filters.append(f"AttendanceType={self.marker}")
            values.append(parameters["AttendanceType"])
        return filters, values

    @staticmethod
    def _positive_integer(value, default):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return default
        return value if value > 0 else default

    @staticmethod
    def _rows(cursor):
        columns = tuple(item[0] for item in cursor.description)
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
