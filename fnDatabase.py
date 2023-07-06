import mysql
import JSForm

host = "192.168.3.200"
database = "ChurchDB"
user = "church"
password = "Church99"

def fnResetAutoIncrement(host,database,user,password):
    ChurchDB = JSForm.clsDB(host, database, user, password)

    sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = '{}';".format(database)
    cursor = ChurchDB.DBConnection.cursor()
    try:
        cursor.execute(sql)
    except Exception as ex:
        print("sql error {err}:{sql} ".format(err=ex, sql=sql))
    tbls = cursor.fetchall()
    
    for t in tbls:
        print (t[0])
        sql = "ALTER TABLE {} AUTO_INCREMENT = 1;".format(t[0])
        try:
            cursor.execute(sql)
        except Exception as ex:
            print("sql error {err}:{sql} ".format(err=ex, sql=sql))

fnResetAutoIncrement(host,database,user,password)