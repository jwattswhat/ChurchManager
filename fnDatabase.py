"""Legacy database helper retained for inventory; active startup uses fnCMargParse."""

import mysql
import JSForm

host = "192.168.3.200"
database = "ChurchDB"
user = "church"
password = None

def fnResetAutoIncrement(host,database,user,password):
    ChurchDB = JSForm.clsDB(host, database, user, password)

    sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = '{}' ORDER BY table_name;".format(database)
    cursor = ChurchDB.DBConnection.cursor()
    try:
        cursor.execute(sql)
    except Exception as ex:
        print("sql error {err}:{sql} ".format(err=ex, sql=sql))
    tbls = cursor.fetchall()
    
    for t in tbls:
        sql = "ALTER TABLE {} AUTO_INCREMENT = 1;".format(t[0])
        print (sql)
        try:
            cursor.execute(sql)
        except Exception as ex:
            print("sql error {err}:{sql} ".format(err=ex, sql=sql))

fnResetAutoIncrement(host,database,user,password)
