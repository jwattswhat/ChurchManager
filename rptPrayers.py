"""Generate the Sunday prayer-request text file."""

import fnCMargParse
from churchmanager_mode import resolve_database
from report_support import (
    connect_report, get_today, load_report_config, open_text_file, write_lines,
)
from sunday_content_rules import occurs_in_service_week, service_week


def build_prayer_lines(rows, report_date):
    lines = ["Service Week Beginning {}".format(report_date.strftime("%m/%d/%Y"))]
    old_category = None
    for row in rows:
        category = row[1]
        if category != old_category:
            old_category = category
            lines.append(category)
        lines.append("\t{}".format(row[2]))
    return lines


def main(argv=None):
    config = load_report_config()
    settings = fnCMargParse.CMargs(
        "rptPrayers", "Sunday Prayers",
        ["server", "database", "user", "test_mode", "reportdate", "churchid"],
        argv=argv,
    )
    settings = resolve_database(settings, config, resolve_credentials=False)
    report_date = get_today(config, settings.get("reportdate"))
    week_start, week_end = service_week(report_date)
    _app, database = connect_report(settings)
    cursor = database.DBConnection.cursor()
    cursor.execute(
        "SELECT ID,PrayerCategory,RequestFor,ScheduleRule,StartDate,EndDate "
        "FROM rpt_sunday_prayer "
        "WHERE ChurchID=%s AND (StartDate IS NULL OR StartDate <= %s) "
        "AND (EndDate IS NULL OR EndDate >= %s) "
        "ORDER BY PrayerCategory,RequestFor",
        (settings["churchid"],week_end,week_start),
    )
    rows = [row for row in cursor.fetchall() if occurs_in_service_week(row[3],report_date,row[4],row[5])]
    output = write_lines("prayers.txt", build_prayer_lines(rows, week_start))
    open_text_file(output)
    return output


if __name__ == "__main__":
    main()
