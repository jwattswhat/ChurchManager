import clsDB
from clsOption import OPTION
import mysql

def conditionCONFIG(condition):
    pos = 0
    while True:
        start = condition.find("{OPTION",pos)
        if start == -1:
            break
        end = condition.find("}",start)
        c1 = condition.find(":",start)
        c2 = condition.find(":",c1+1) 
        optionfor = condition[c1+1:c2]
        optionvalue = condition[c2+1:end]
        pos = start
        condition = condition.replace(condition[start:end+1],'"'+OPTION.get_Option_Value(optionfor,optionvalue)+'"',1)
    return condition

condition = "ID = {id} AND Lectionary = {OPTION:Lectionary:Current} ii = {OPTION:Lectionary:Current}"

ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
OPTION.set_Option_DBConnection(ChurchDBConnection)

print (conditionCONFIG(condition))


