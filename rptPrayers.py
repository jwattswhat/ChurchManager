from re import S
import mysql
from datetime import datetime, date
import calendar
import subprocess
import argparse

import JSForm



def readallrecords(table):
    SQL = JSForm.clsSQL(ChurchDB.DBConnection, table)
    sql = SQL.select()
    cursor = ChurchDB.DBConnection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def sunday(dt):
    wk = 6
    deltime = wk - dt.weekday()
    return dt + datetime.timedelta(deltime)

cmparser = argparse.ArgumentParser(
    prog="rptAnnouncement", description="Church Manager v0.1"
)
cmparser.add_argument("-r", "--reportdate", type=str, default="")

args = cmparser.parse_args()
# print(args.server,args.database,args.user,args.password)


reportdate = args.reportdate
if not reportdate:
    dt = datetime.now()
else:
    dt = datetime.strptime(reportdate,"%m/%d/%Y")

TODAY = dt
# print("Today",TODAY)
FIRSTDAY = JSForm.date_to_datetime(TODAY.replace(day=1))
# print("First Day",FIRSTDAY)
LASTDAY = JSForm.date_to_datetime(
    date(TODAY.year, TODAY.month, calendar.monthrange(TODAY.year, TODAY.month)[1])
)
# print("Last Day",LASTDAY)
SUNDAY = JSForm.next_weekday(TODAY, 6)
# print ("Current Sunday", SUNDAY)
SUNDAYS = []
SUNDAYS.append(
    JSForm.date_to_datetime(JSForm.next_weekday(FIRSTDAY, 6))
)  # first sunday
SUNDAYS.append(
    JSForm.date_to_datetime(JSForm.next_weekday(SUNDAYS[0], 6))
)  # second sunday
SUNDAYS.append(
    JSForm.date_to_datetime(JSForm.next_weekday(SUNDAYS[1], 6))
)  # third sunday
SUNDAYS.append(
    JSForm.date_to_datetime(JSForm.next_weekday(SUNDAYS[2], 6))
)  # fourth sunday
FIFTHSUNDAY = JSForm.date_to_datetime(
    JSForm.next_weekday(SUNDAYS[3], 6)
)  # fifth sunday
if FIFTHSUNDAY > LASTDAY:
    if SUNDAY > SUNDAYS[3]:
        FIFTHSUNDAY = SUNDAY
    else:
        FIFTHSUNDAY = None
SUNDAYS.append(FIFTHSUNDAY)
td = ""
for lastsunday in range(0,len(SUNDAYS)):
    if SUNDAYS[lastsunday] == None:
        break
    if SUNDAYS[lastsunday] <= TODAY <= SUNDAYS[lastsunday+1]:
        match lastsunday:
            case 0:
                td = "First = 1 AND"
            case 1:
                td = "Second = 1 AND"
            case 2:
                td = "Third = 1 AND"
            case 3:
                td = "Fourth = 1 AND"
            case 5:
                td = "Fifth = 1 AND"
        break


ChurchDB = JSForm.clsDB("192.168.3.200", "ChurchDB", "church", "Church99")

PR_ID = 0
PR_CHURCHID = 1
PR_REQUEST = 2
PR_CATEGORY = 3
PR_REQUESTFOR = 4
PR_REQUESTBY = 5
PR_CONTINUOUS = 6
PR_FIRSTSUNDAY = 7
PR_SECONDSUNDAY = 8
PR_THIRDSUNDAY = 9
PR_FOURTHSUNDAY = 10
PR_FIFTHSUNDAY = 11
PR_STARTDATE = 12
PR_ENDDATE = 13
PR_NOTE = 14

prayers = readallrecords(
    {"name": "tblPrayer", 
     "fields": ["*"], 
     "condition": "{Sunday} ((Continuous = 1) OR (NOW() BETWEEN StartDate AND EndDate))".format(Sunday=td),
     "orderby": "PrayerCategory, RequestFor"}
)

prfmt = "\t{FOR}" #\t{REQ}\t{NOTE}" # too much data
prfile = []
oldcat = ""
for p in range(len(prayers)):
    if oldcat != prayers[p][PR_CATEGORY]:
        oldcat = prayers[p][PR_CATEGORY]
        prfile.append(prayers[p][PR_CATEGORY])

    req = ""
    if prayers[p][PR_REQUEST] != prayers[p][PR_CATEGORY]:
        req = prayers[p][PR_REQUEST]
    if prayers[p][PR_NOTE] == None:
        PrNote = ""
    else:
        PrNote = prayers[p][PR_NOTE]
    prfile.append(prfmt.format(FOR=prayers[p][PR_REQUESTFOR])) #REQ=req)) #, ,NOTE=PrNote))

with open("prayers.txt", "w") as osfile:
    for l in range(len(prfile)):
        osfile.write(prfile[l] + "\r")
subprocess.Popen(["notepad", "prayers.txt"])
