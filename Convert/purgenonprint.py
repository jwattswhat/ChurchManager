import unicodedata, re, itertools, sys
import mariadb
import clsDB
import mysql.connector
import os

def remove_control_chars(s):
    return control_char_re.sub('', s)

def replaceit(field):
    before = field
    after = field
    for d in deletelist:
        after = after.replace(d[0],d[1])
    after = os.linesep.join([s for s in after.splitlines() if s])
    print (before==after)
    return after

ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)

all_chars = (chr(i) for i in range(sys.maxunicode))
categories = {'Cc'}

#control_chars = ''.join(c for c in all_chars if unicodedata.category(c) in categories)
# or equivalently and much more efficiently
control_chars = ''.join(map(chr, itertools.chain(range(0x00,0x20), range(0x7f,0xa0))))

control_char_re = re.compile('[%s]' % re.escape(control_chars))

sql = "SELECT ID, Theme,Introit,HymnSug FROM tblPropers;"# where ID=313;"
deletelist = [
            ["<div>",""],
            ["</div>",""],
            ["<strong>",""],
            ["</strong>",""],
            ["&nbsp;",""],
            ["&quot;",""],
            ["–","-"],
            ["\"","'"]
            ]
fields = ["Theme","Introit","HymnSug"]
cursor = ChurchDBConnection.cursor()
cursor.execute(sql)
rows = cursor.fetchall()
for row in rows:
    if row[1] == None and row[2] == None and row[3] == None:
        continue
    theme=""
    introit = ""
    hymnsug = ""
    if row[1] != None:
        theme = replaceit(row[1])
    if row[2] != None:
        introit = replaceit(row[2])
    if row[3] != None:
        hymnsug = replaceit(row[3])
    updatesql = 'UPDATE tblPropers SET theme = "{theme}", introit="{introit}", hymnsug="{hymnsug}" WHERE ID={ID};'.format(
    theme=theme,
    introit=introit,
    hymnsug=hymnsug,
    ID=str(row[0]))
    updatecursor = ChurchDBConnection.cursor()
    updatecursor.execute(updatesql)
updatecursor.close()

