message = """
If you need Private Communion for any reason, a pending hospitalization, having a bad week, or you need the gifts that God gives in His Holy Supper. Please know I am available any time. It is part of my Divine Call to this congregation to administer the Sacrament. Call or text to make an appointment or drop in during office hours. I would be glad to help.
"""
MAXMESSLEN = 200
continuemess = False
def splitbymax(m,ml):
    if len(m) <= ml:
        return [m]
    i = ml
    while m[i] != " ":
        i-=1
    print (m[0:i], m[i+1:len(m)])
    return [m[0:i], m[i:len(m)]]

splitmessage = splitbymax(message,MAXMESSLEN)
for i in range(0,len(splitmessage)):
    print (splitmessage[i])
