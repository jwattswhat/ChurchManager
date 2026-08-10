"""Generate the Sunday announcements text file."""

import fnCMargParse
from churchmanager_mode import resolve_database
from report_support import connect_report, get_today, load_report_config, open_text_file, week_column, write_lines


def build_announcement_lines(rows, report_date):
    lines = ["Report Run {}".format(report_date.strftime("%m/%d/%Y"))]
    for row in rows:
        lines.append((row[4] or "").replace("[", "").replace("]", ""))
    return lines


def main(argv=None):
    config = load_report_config()
    settings = fnCMargParse.CMargs(
        "rptAnnouncement", "Sunday Announcements",
        ["server", "database", "user", "test_mode", "jsform_database", "reportdate"],
        argv=argv,
    )
    settings = resolve_database(settings, config)
    report_date = get_today(config, settings.get("reportdate"))
    column = week_column(report_date)
    _app, database = connect_report(settings)
    cursor = database.DBConnection.cursor()
    cursor.execute(
        "SELECT * FROM tblAnnouncement WHERE eDisplayOnly = 0 AND "
        "(StartDate IS NULL OR StartDate <= %s) AND "
        "(EndDate IS NULL OR EndDate >= %s) AND {} = 1 "
        "ORDER BY Priority, Label, RequestBy".format(column),
        (report_date, report_date),
    )
    output = write_lines(
        "announcement.txt", build_announcement_lines(cursor.fetchall(), report_date)
    )
    open_text_file(output)
    return output


if __name__ == "__main__":
    main()
