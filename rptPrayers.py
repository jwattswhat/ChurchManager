"""Generate the Sunday prayer-request text file."""

import fnCMargParse
from churchmanager_mode import resolve_database
from report_support import (
    connect_report, get_today, get_week_of_month, load_report_config,
    open_text_file, week_column, write_lines,
)


def build_prayer_lines(rows, report_date):
    lines = ["Report Run {}".format(report_date.strftime("%m/%d/%Y"))]
    old_category = None
    for row in rows:
        category = row[3]
        if category != old_category:
            old_category = category
            lines.append(category)
        lines.append("\t{}".format(row[4]))
    return lines


def main(argv=None):
    config = load_report_config()
    settings = fnCMargParse.CMargs(
        "rptPrayers", "Sunday Prayers",
        ["server", "database", "user", "test_mode", "jsform_database", "reportdate"],
        argv=argv,
    )
    settings = resolve_database(settings, config)
    report_date = get_today(config, settings.get("reportdate"))
    column = week_column(report_date)
    _app, database = connect_report(settings)
    cursor = database.DBConnection.cursor()
    cursor.execute(
        "SELECT * FROM tblPrayer WHERE "
        "(StartDate IS NULL OR StartDate <= %s) AND "
        "(EndDate IS NULL OR EndDate >= %s) AND {} = 1 "
        "ORDER BY PrayerCategory, RequestFor".format(column),
        (report_date, report_date),
    )
    output = write_lines("prayers.txt", build_prayer_lines(cursor.fetchall(), report_date))
    open_text_file(output)
    return output


if __name__ == "__main__":
    main()

