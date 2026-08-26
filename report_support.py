"""Shared, import-safe helpers for ChurchManager command-line reports."""

import json
import os
from datetime import date, datetime
from pathlib import Path


CONFIG_PATH = Path(__file__).with_name("churchmanager.json")
WEEK_COLUMNS = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth"}


def load_report_config(path=CONFIG_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def get_today(config, requested=None):
    """Resolve a requested report date, configured test override, or today."""
    value = requested
    if not value or str(value).casefold() == "now":
        value = config.get("testing", {}).get("override_today")
    if value:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    return date.today()


def get_week_of_month(value):
    first_day = value.replace(day=1)
    return (value.day + first_day.weekday() - 1) // 7 + 1


def week_column(value):
    return WEEK_COLUMNS[get_week_of_month(value)]


def connect_report(settings):
    """Create the wx application and JSForm-owned database connection."""
    import wx
    import JSForm

    wx_app = wx.App(0)
    database = JSForm.clsDB(
        settings["server"], settings["database"], settings["user"],
        settings["password"], settings["jsform_database"],
    )
    return wx_app, database


def write_lines(path, lines):
    output = Path(path)
    output.write_text("\r".join(lines) + "\r", encoding="utf-8")
    return output


def open_text_file(path):
    os.startfile(str(Path(path).resolve()))

