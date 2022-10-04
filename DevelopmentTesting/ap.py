import argparse

parser = argparse.ArgumentParser(
    prog="rptWorshipPlanningWorksheet.py", description="Worship Planning Worksheet"
)
parser.add_argument("--version", action="version", version="%(prog)s 0.1")
parser.add_argument(
    "-I",
    "--ID",
    dest="ID",
    action="store",
    type=int,
    nargs=1,
    help="override the temperature read from the DS18B20 probe",
)
args = parser.parse_args()
if args.ID:
    print(args.ID)
