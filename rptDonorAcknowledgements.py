import argparse
import mysql
import mysql.connector
import JSForm.clsDB
cmparser = argparse.ArgumentParser(
    prog="rptDonorAcknowledgments", description="Donor Acknowledgement Report"
)
cmparser.add_argument("-s", "--server", type=str, default="localhost")
cmparser.add_argument("-d", "--database", type=str, default="ChurchDB")
cmparser.add_argument("-u", "--user", type=str)
cmparser.add_argument("-p", "--password", type=str)

args = cmparser.parse_args()
# print(args.server,args.database,args.user,args.password)


host = args.server
database = args.database
user = args.user
password = args.password



ChurchDB = JSForm.clsDB(host, database, user, password)
cursor = ChurchDB.DBConnection.cursor()
SQL = "SELECT g.Amount, d.Name, d.Address, d.Address2, d.City, d.State, d.Zip FROM tblDonorgift as g INNER JOIN tblDonor as d on g.DonorID = d.ID WHERE g.Acknowledged = 0"
cursor.execute(SQL)
rows = cursor.fetchall()
txtfile = open("C:\\Users\\jonat\\Documents\\PythonProjects\\ChurchManager\\Reports\\acknowledgements.csv","w")
for r in range(0,len(rows)):
    l = ""
    for c in range(0,len(rows[r])):
        if l != "":
            l = l + ","
        l = l + str(rows[r][c])
    txtfile.write (l+"\n")
txtfile.close()
