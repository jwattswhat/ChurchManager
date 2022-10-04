# !/usr/bin/env python3
import mysql
import clsDB

CONTROLDESCRIPTION = {
    "HymnID": {
        "type": "ComboBox",
        "SQL": "SELECT h.ID,concat(hl.HymnalPrefix, h.Hymn, ' ', h.Title) FROM tblHymnal hl JOIN tblHymn h ON h.HymnalID = hl.ID",
        "name": "HymnID",
    },

    "ServiceID": {
        "type": "StaticText",
        "SQL": "SELECT DateTime FROM tblService WHERE ID = <<where>>",
        "name": "DateTime",
    },

    "lookuptest": {
        "type" : "StaticText",
        "SQL" : "SELECT ConfigValue FROM tblConfig WHERE ConfigType = 'LectionarySeriesYear';",
        "name": "lookuptest",
    }
}


DB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
DBConnection = mysql.connector.connect(**DB.DB)

def get_combobox_choices(key,sql,type):
        choicesdict = {}
        cursor = DBConnection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            choicesdict.update({row[0]: row[1]})
        return choicesdict

def lookup(key):
    cursor = DBConnection.cursor()
    sql = CONTROLDESCRIPTION[key]['SQL']
    whereloc = sql.find("<<where>>")
    if whereloc != -1:
        where = '2'
        sql = sql.replace("<<where>>",where)
    cursor.execute(sql)
    row = cursor.fetchone()
    return row[0]

for key in CONTROLDESCRIPTION:
    if CONTROLDESCRIPTION[key]['type'] == "StaticText":
        if "SQL" in CONTROLDESCRIPTION[key]:
            print (lookup(key))

    if CONTROLDESCRIPTION[key]['type'] == "ComboBox":
        if "SQL" in CONTROLDESCRIPTION[key]:
            print (get_combobox_choices(key,CONTROLDESCRIPTION[key]['SQL'],CONTROLDESCRIPTION[key]['type']))



