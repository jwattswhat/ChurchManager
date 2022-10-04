# !/usr/bin/env python3
# 	CMworship.py  Church Manager - Worship v0.1

import wx
import pprint
import json

pp = pprint

list = ['Hymns, Selected','Worship Planning, Complete','Worship Planning, Printed','Participents Scheduled','Particpients Notified','Bulletin, Prepared', 'Bulletin, Printed','Bulletin, Posted to Website','Sermon, Prepared','Sermon, Printed','Sermon, Posted to Blog','Prayers, Printed']
pp.pprint (list)

cklist = {}
for x in list:
    cklist.update({x:False})

pp.pprint (cklist)

j = json.dumps(cklist)
pp.pprint(j)

c = json.loads(j)
pp.pprint(c)