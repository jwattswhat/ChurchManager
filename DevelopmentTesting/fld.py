import mysql
import clsDB

ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)



cursor = ChurchDBConnection.cursor()
sql = "SELECT ID,Theme,Introit,HymnSug,Note FROM tblPropers;"
cursor.execute(sql)
rows = cursor.fetchall()
for r in rows:
    print (r)
    cursor2 = ChurchDBConnection.cursor()
    th = r[1]
    if th != None:
        th.replace("/n","/r/n") 
        sql = "UPDATE tblPropers SET Theme = '{th}' WHERE ID = {id};".format(th=th,id=r[0])
        try:
            cursor.execute(sql)
        except:
            print ("error",r)
    int = r[2]
    if int != None:
        int.replace("/n","/r/n") 
        sql = "UPDATE tblPropers SET Introit = '{int}' WHERE ID = {id};".format(int=int,id=r[0])
        try:
            cursor.execute(sql)
        except:
            print ("error",r)
    hy = r[3]
    if hy != None:
        hy.replace("/n","/r/n") 
        sql = "UPDATE tblPropers SET HymnSug = '{hy}' WHERE ID = {id};".format(hy=hy,id=r[0])
        try:
            cursor.execute(sql)
        except:
            print ("error",r)
    no = r[4]
    if no != None:
        no.replace("/n","/r/n") 
        sql = "UPDATE tblPropers SET Note = '{no}' WHERE ID = {id};".format(no=no,id=r[0])
        try:
            cursor.execute(sql)
        except:
            print ("error",r)
    pass      
