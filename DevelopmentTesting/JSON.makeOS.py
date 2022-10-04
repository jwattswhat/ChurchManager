import json
import pprint
from typing import OrderedDict
import mysql
import mysql.connector

import clsDB
import clsSQL
from clsConfig import CONFIG
from clsOption import OPTION

jsonname = "os.json"
f = open(
    jsonname,
)
jsonos = json.load(f)
# pprint.pprint(jsonos)

sorttable = {
    "Service": {10: "Date", 20: "Time", 30: "Title", 40: "OrderofService"},
    "Lines": {
        0: "Entrance",
        10: "Kyrie",
        20: "Gloira",
        30: "OfTheDay",
        40: "Alleluia",
        50: "Communion",
        60: "Sanctus",
        70: "AgnusDei",
        80: "NuncDimittus",
        90: "Closing",
    },
}
orderedjsonos = OrderedDict()

orderedjsonos["Service"] = OrderedDict()
for o in sorttable["Service"]:
    orderedjsonos["Service"][sorttable["Service"][o]] = jsonos["Service"][
        sorttable["Service"][o]
    ]

orderedjsonos["Service"]["Lines"] = OrderedDict()
for o in sorttable["Lines"]:
    orderedjsonos["Service"]["Lines"][sorttable["Lines"][o]] = jsonos["Service"][
        "Lines"
    ][sorttable["Lines"][o]]


ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
CONFIG.set_Config_DBConnection(ChurchDBConnection)
OPTION.set_Option_DBConnection(ChurchDBConnection)

tblservice = {"name": "tblService", "fields": ["*"], "condition": "ID = 4"}

service = clsDB.clsRecord(ChurchDBConnection, tblservice)
service.load_records(tblservice)
# print ("Service")
# pprint.pprint(service._record)

tblhymnusage = {"name": "vwHymnUsage", "fields": ["*"], "condition": "ServiceID = 4"}
hymnusage = clsDB.clsRecord(ChurchDBConnection, tblhymnusage)
hymnusage.load_records(tblhymnusage)
# print("Hymns")
# pprint.pprint(hymnusage._record)

for r in range(len(hymnusage._record)):
    # print (hymnusage._record[r]["UsedAs"])
    # pprint.pprint(jsonos["Service"]["Lines"][hymnusage._record[r]["UsedAs"]])
    orderedjsonos["Service"]["Lines"][hymnusage._record[r]["UsedAs"]][
        "Page"
    ] = hymnusage._record[r]["Hymn"]
    orderedjsonos["Service"]["Lines"][hymnusage._record[r]["UsedAs"]][
        "Title"
    ] = hymnusage._record[r]["Title"]
    orderedjsonos["Service"]["Lines"][hymnusage._record[r]["UsedAs"]][
        "File"
    ] = hymnusage._record[r]["File"]

with open("OSnew.json", "w") as outfile:
    json.dump(orderedjsonos, outfile)
