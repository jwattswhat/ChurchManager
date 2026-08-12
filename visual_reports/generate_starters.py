"""Generate standardized, editable starter definitions from the official inventory."""

import json
from pathlib import Path

from visual_reports.report_inventory import SPECS


ROOT = Path(__file__).resolve().parent
DEFINITIONS = ROOT / "definitions"


def starter(spec):
    landscape = spec.orientation == "landscape"
    content_width = 720 if landscape else 540
    supplied = sum(column.width for column in spec.columns)
    scale = content_width / supplied
    columns = []
    for column in spec.columns:
        item = {
            "name": column.field, "label": column.label, "collection": "records",
            "field": column.field, "width": round(column.width * scale, 2),
        }
        if column.data_type != "text":
            item["format"] = column.data_type
        if column.align != "left":
            item["align"] = column.align
        columns.append(item)
    first_sort = spec.order_by.split(",", 1)[0].strip().split()
    report = {
        "schema_version": 1, "name": spec.code, "title": spec.title,
        "dataset": f"churchmanager.{spec.code.lower()}", "datasetversion": 1,
        "pagesize": "letter", "orientation": spec.orientation,
        "margins": {"top": 30, "right": 36, "bottom": 30, "left": 36},
        "theme": "churchmanager.standard",
        "emptytext": "No records match the selected criteria.",
        "bands": {
            "ReportHeader": {"type": "reportheader", "height": 92},
            "PageHeader": {"type": "pageheader", "height": 8, "repeat": True},
            "Detail": {"type": "detail", "height": 42},
            "PageFooter": {"type": "pagefooter", "height": 24, "repeat": True},
        },
        "sort": [{
            "collection": "records", "field": first_sort[0],
            "direction": "descending" if len(first_sort) > 1 and first_sort[1].upper() == "DESC" else "ascending",
        }],
    }
    controls = {
        "ChurchLogo": {"type": "image", "band": "ReportHeader", "position": [0, 0], "size": [62, 62], "collection": "church", "field": "Logo"},
        "ChurchName": {"type": "text", "band": "ReportHeader", "position": [72, 2], "size": [content_width - 72, 22], "collection": "church", "field": "Church", "fontsize": 15, "bold": True, "align": "center"},
        "ReportTitle": {"type": "systemtext", "band": "ReportHeader", "position": [72, 29], "size": [content_width - 72, 20], "systemvalue": "report_title", "fontsize": 13, "bold": True, "align": "center"},
        "Parameters": {"type": "text", "band": "ReportHeader", "position": [72, 54], "size": [content_width - 180, 16], "collection": "parameters", "field": "Display", "fontsize": 8, "color": "#555555"},
        "RunDate": {"type": "systemtext", "band": "ReportHeader", "position": [content_width - 100, 54], "size": [100, 16], "systemvalue": "run_date", "prefix": "Run: ", "fontsize": 8, "align": "right", "color": "#555555"},
        "HeaderRule": {"type": "line", "band": "PageHeader", "position": [0, 4], "size": [content_width, 1], "bordercolor": "#6D7780", "borderwidth": 0.7},
        "Records": {"type": "table", "band": "Detail", "position": [0, 0], "size": [content_width, 40], "repeatcollection": "records", "columns": columns},
        "FooterLine": {"type": "line", "band": "PageFooter", "position": [0, 0], "size": [content_width, 1], "bordercolor": "#808080", "borderwidth": 0.5},
        "FooterCode": {"type": "systemtext", "band": "PageFooter", "position": [0, 6], "size": [content_width / 2, 14], "systemvalue": "report_code", "prefix": "ChurchManager report ", "fontsize": 8, "color": "#555555"},
        "PageNumber": {"type": "systemtext", "band": "PageFooter", "position": [content_width - 90, 6], "size": [90, 14], "systemvalue": "page_number", "prefix": "Page ", "fontsize": 8, "align": "right", "color": "#555555"},
    }
    return {f"{spec.code}REPORT": {"REPORT": report, "CONTROLS": controls}}


def generate():
    DEFINITIONS.mkdir(parents=True, exist_ok=True)
    for spec in SPECS:
        path = DEFINITIONS / f"{spec.code}.json"
        path.write_text(json.dumps(starter(spec), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    generate()
