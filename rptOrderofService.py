import argparse
import pprint
from re import L, search
import mysql
import os
from typing import OrderedDict
import json
import subprocess

import JSForm

#   Service Constants
S_ID = 0
S_Date = 2
S_Propers = 3
S_OS = 6

#   Order of Service Constants
OS_Line = 2
OS_Title = 3
OS_Content = 4
OS_Page = 5
OS_File = 6

#   Propers Constants
P_ID = 0

#   Hymn Usage Constants
HU_ID = 0
HU_ChurchID = 1
HU_ServiceID = 2
HU_HymnID = 3
HU_Usage = 4
HU_Note = 5

#   Hymn Constants
H_Hymn = 2
H_Title = 3
H_File = 6

#   Reading Constants
R_Reading = 2
R_Reference = 3


def getimbedname(arg):
    st = arg.find("{")
    en = arg.find("}")
    if st == -1:
        return None
    return arg[st + 1 : en]


def readallrecords(table):
    SQL = JSForm.clsSQL(ChurchDB.DBConnection, table)
    sql = SQL.select()
    cursor = ChurchDB.DBConnection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def readonerecord(table):
    SQL = JSForm.clsSQL(ChurchDB.DBConnection, table)
    sql = SQL.select()
    cursor = ChurchDB.DBConnection.cursor()
    cursor.execute(sql)
    return cursor.fetchone()


def searchrecrods(string, records):
    for rec in records:
        if string in rec:
            return rec
    return None


parser = argparse.ArgumentParser(
    prog="rptOrderofServcie.py", description="OrderofService"
)
parser.add_argument("--version", action="version", version="%(prog)s 0.1")
parser.add_argument(
    "-I",
    "--ID",
    dest="ID",
    action="store",
    type=int,
    nargs=1,
    help="Enter Service ID",
)
args = parser.parse_args()
if not args.ID:
    print("no Service ID")
    exit()

ChurchDB = JSForm.clsDB("localhost", "ChurchDB", "church", "Church99")
JSForm.CONFIG.set_Config_DBConnection(ChurchDB.DBConnection)

#   Service

srow = readonerecord(
    {
        "name": "tblService",
        "fields": ["*"],
        "condition": "ID = {ID}".format(ID=args.ID[0]),
    }
)
# print ("Service")
# pprint.pprint(srow)
# print()

#   Order of Service

osr = readallrecords(
    {
        "name": "tblOrderofService",
        "fields": ["*"],
        "condition": "OrderofService = '{OS}'".format(OS=srow[S_OS]),
        "orderby": "Line",
    }
)

#   replace special characters
osrows = []
replacevalues = {"{tab}":"\t"}
for rep in replacevalues:
    for row in range(len(osr)):
        osrows.append([])
        for col in range(len(osr[row])):
            if col == 4:
                osrows[row].append(osr[row][col].replace(rep,replacevalues[rep]))
            else:
                osrows[row].append(osr[row][col])

# print ("Order of Service")
# pprint.pprint(osrows)
# rint()

#   Hymns

hrows = readallrecords(
    {
        "name": "tblHymnUsage",
        "fields": ["*"],
        "condition": "ServiceID = {serviceid}".format(serviceid=srow[S_ID]),
    }
)
# print("Hymns")
# pprint.pprint(hrows)
# print()

#   propers

prow = readonerecord(
    {
        "name": "tblPropers",
        "fields": ["*"],
        "condition": "ID = {PropersID};".format(PropersID=srow[S_Propers]),
    }
)
# print("propers")
# pprint.pprint(prow)
# print()

#   Readings

rrows = readallrecords(
    {
        "name": "tblAltReading",
        "fields": ["*"],
        "condition": "ServiceID={serviceid}".format(serviceid=args.ID[0]),
    }
)
if len(rrows) == 0:
    rrows = readallrecords(
        {
            "name": "tblReading",
            "fields": ["*"],
            "condition": "PropersID={propersid}".format(propersid=prow[P_ID]),
        }
    )
# print("Readings")
# pprint.pprint(rrows)
# print()

#   Main Loop
jsondict = OrderedDict()
jsondict["Service"] = OrderedDict()
prnt = {}
# jsondict["Service"]["Date"] = srow[S_Date]
jsondict["Service"]["Title"] = srow[4]

jsondict["Service"]["Lines"] = OrderedDict()

for row in osrows:
    imbed = getimbedname(row[OS_Content])
    if imbed == None:
        prnt[row[OS_Line]] = row[OS_Content]
        if row[OS_File] != None:
            jsondict["Service"]["Lines"][row[OS_Title]] = {}
            jsondict["Service"]["Lines"][row[OS_Title]]["Page"] = str(row[OS_Page])
            jsondict["Service"]["Lines"][row[OS_Title]]["Title"] = row[OS_Title]
            jsondict["Service"]["Lines"][row[OS_Title]]["File"] = row[OS_File]
        continue
    match imbed:

        #   Hymns
        case ("Entrance" | "Office Hymn" | "Of the Day" | "Communion" | "Closing"):
            useage = searchrecrods(imbed, hrows)
            sql = "SELECT * FROM tblHymn WHERE ID = {id};".format(id=useage[HU_HymnID])
            cursor = ChurchDB.DBConnection.cursor()
            cursor.execute(sql)
            hymn = cursor.fetchone()
            prnt[row[OS_Line]] = row[OS_Content].replace(
                "{" + imbed + "}", hymn[H_Hymn]
            )
            jsondict["Service"]["Lines"][imbed] = {}
            jsondict["Service"]["Lines"][imbed]["Page"] = str(hymn[H_Hymn])
            jsondict["Service"]["Lines"][imbed]["Title"] = hymn[H_Title]
            jsondict["Service"]["Lines"][imbed]["File"] = hymn[H_File]

            continue

        #   Readings
        case ("Psalm" | "First" | "Second" | "Third" | "Old Testament" | "Epistle" | "Gospel"):
            reading = searchrecrods(imbed, rrows)
            if reading != None:
                prnt[row[OS_Line]] = row[OS_Content].replace(
                    "{" + imbed + "}", reading[R_Reference]
                )
            continue

        case _:
            print("other", imbed)
            continue
OS_Line += 1
#prnt[
#    srow[OS_Line]
#] = "Liturgy Used by Permission Concordia Publishing House #{License}".format(
#    License=JSForm.CONFIG.get_Config_Value("License", "Liturgy")
#)

with open("OS.json", "w") as jsonfile:
    json.dump(jsondict, jsonfile)

with open("OS.txt", "w") as osfile:
    for line in prnt:
        osfile.write(prnt[line].replace("\\t", "\t") + "\r")
subprocess.Popen(["notepad", "OS.txt"])
subprocess.Popen(["notepad", "OS.json"])
