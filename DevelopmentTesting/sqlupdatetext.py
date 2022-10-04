import datetime
table = "tblBugs"
data = {"ID":0,"Description":"Some Description","Date":"01/01/2020","NoData":None,"Boolean":True}
value = []
keys = data.keys()
for k in keys:
    if k == "ID":
        continue
    if data[k] != None:
        value.append("{key}='{value}'".format(key=k,value=data[k]))
values = ",".join(value)
print (values)

sql = "UPDATE {table} SET {values} WHERE ID={id};".format(table=table,values=values,id=data["ID"])

print (sql)

