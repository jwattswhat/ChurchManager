import datetime

data = {"ID":0,"Description":"Description","DateTime":"01/01/2020","NoData":"None"}
data.pop("ID")
for d in data.copy():
    if data[d] == "None":
        data.pop(d)
ky = ",".join(data.keys())
dt = "','".join(data.values())
sql = "INSERT INTO tblTable ({keys}) VALUES ('{values}');".format(keys = ky, values = dt)

print (sql)

