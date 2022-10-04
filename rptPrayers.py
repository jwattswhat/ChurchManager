from re import S
import mysql
from datetime import datetime, date
import calendar
import subprocess

import clsDB
import clsSQL
from clsConfig import CONFIG
import fnUtil


def readallrecords(table):
    SQL = clsSQL.clsSQL(ChurchDBConnection, table)
    sql = SQL.select()
    cursor = ChurchDBConnection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def sunday(dt):
    wk = 6
    deltime = wk - dt.weekday()
    return dt + datetime.timedelta(deltime)


TODAY = datetime.now()
# print("Today",TODAY)
FIRSTDAY = fnUtil.date_to_datetime(TODAY.replace(day=1))
# print("First Day",FIRSTDAY)
LASTDAY = fnUtil.date_to_datetime(
    date(TODAY.year, TODAY.month, calendar.monthrange(TODAY.year, TODAY.month)[1])
)
# print("Last Day",LASTDAY)
SUNDAY = fnUtil.next_weekday(TODAY, 6)
# print ("Current Sunday", SUNDAY)
SUNDAYS = []
SUNDAYS.append(
    fnUtil.date_to_datetime(fnUtil.next_weekday(FIRSTDAY, 6))
)  # first sunday
SUNDAYS.append(
    fnUtil.date_to_datetime(fnUtil.next_weekday(SUNDAYS[0], 6))
)  # second sunday
SUNDAYS.append(
    fnUtil.date_to_datetime(fnUtil.next_weekday(SUNDAYS[1], 6))
)  # third sunday
SUNDAYS.append(
    fnUtil.date_to_datetime(fnUtil.next_weekday(SUNDAYS[2], 6))
)  # fourth sunday
FIFTHSUNDAY = fnUtil.date_to_datetime(
    fnUtil.next_weekday(SUNDAYS[3], 6)
)  # fifth sunday
if FIFTHSUNDAY > LASTDAY:
    FIFTHSUNDAY = None
SUNDAYS.append(FIFTHSUNDAY)
# for i in range(len(SUNDAYS)):
# print (i+1, SUNDAYS[i])

# print ("Next Sunday",SUNDAY)

ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)

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
    {"name": "tblPrayer", "fields": ["*"], "orderby": "PrayerCategory, RequestFor"}
)

prfmt = "\t{FOR}\t{REQ}"
prfile = []
oldcat = ""
for p in range(len(prayers)):
    if oldcat != prayers[p][PR_CATEGORY]:
        oldcat = prayers[p][PR_CATEGORY]
        prfile.append(prayers[p][PR_CATEGORY])

    if prayers[p][PR_CONTINUOUS]:
        startdate = SUNDAY
        enddate = SUNDAY
    else:
        startdate = fnUtil.date_to_datetime(prayers[p][PR_STARTDATE])
        enddate = fnUtil.date_to_datetime(prayers[p][PR_ENDDATE])

    # print (prayers[p][PR_REQUESTFOR])
    thissunday = False
    try:
        s = SUNDAYS.index(SUNDAY) + 1
    except:
        s = None
    if (prayers[p][PR_FIRSTSUNDAY] == 1) and s == 1:
        thissunday = True
    if (prayers[p][PR_SECONDSUNDAY] == 1) and s == 2:
        thissunday = True
    if (prayers[p][PR_THIRDSUNDAY] == 1) and s == 3:
        thissunday = True
    if (prayers[p][PR_FOURTHSUNDAY] == 1) and s == 4:
        thissunday = True
    if (prayers[p][PR_FIFTHSUNDAY] == 1) and s == 5:
        thissunday = True

    if not prayers[p][PR_CONTINUOUS]:
        if thissunday:
            if (startdate < SUNDAY) or (enddate > SUNDAY):
                continue
    if not thissunday:
        continue
    req = ""
    if prayers[p][PR_REQUEST] != prayers[p][PR_CATEGORY]:
        req = prayers[p][PR_REQUEST]
    prfile.append(prfmt.format(REQ=req, FOR=prayers[p][PR_REQUESTFOR]))

with open("prayers.txt", "w") as osfile:
    for l in range(len(prfile)):
        osfile.write(prfile[l] + "\r")
subprocess.Popen(["notepad", "prayers.txt"])
