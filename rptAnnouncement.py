from re import S
import mysql
from datetime import datetime, date
import calendar
import subprocess

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


TODAY = datetime.now()
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

# print ("Next Sunday",SUNDAY)

ChurchDB = JSForm.clsDB("localhost", "ChurchDB", "church", "Church99")

AN_ID = 0
AN_CHURCHID = 1
AN_LABEL = 2
AN_ANNOUNCEMENT = 3
AN_REQUESTBY = 4
AN_CONTINUOUS = 5
AN_FIRSTSUNDAY = 6
AN_SECONDSUNDAY = 7
AN_THIRDSUNDAY = 8
AN_FOURTHSUNDAY = 9
AN_FIFTHSUNDAY = 10
AN_STARTDATE = 11
AN_ENDDATE = 12
AN_NOTE = 13


announcement = readallrecords(
    {"name": "tblAnnouncement", 
     "fields": ["*"], 
     "condition": "{Sunday} ((Continuous = 1) OR (NOW() BETWEEN StartDate AND EndDate))".format(Sunday=td),
     "orderby": "Label, RequestBy"}
)

prfmt = "{ANNOUNCEMENT}" #\t{REQ}\t{NOTE}" # too much data
anfile = []
oldcat = ""
for a in range(len(announcement)):
    #if oldcat != announcement[p][AN_CATEGORY]:
    #    oldcat = announcement[p][AN_CATEGORY]
    #    prfile.append(announcement[p][AN_CATEGORY])

    ann = ""
    #if announcement[a][AN_ANNOUNCEMENT] != announcement[a][AN_CATEGORY]:
    ann = announcement[a][AN_ANNOUNCEMENT]
    if announcement[a][AN_NOTE] == None:
        PrNote = ""
    else:
        PrNote = announcement[a][AN_NOTE]
    anfile.append(prfmt.format(ANNOUNCEMENT=announcement[a][AN_ANNOUNCEMENT])) #REQ=req)) #, ,NOTE=PrNote))

with open("announcement.txt", "w") as osfile:
    for l in range(len(anfile)):
        osfile.write(anfile[l] + "\r")
subprocess.Popen(["notepad", "announcement.txt"])
