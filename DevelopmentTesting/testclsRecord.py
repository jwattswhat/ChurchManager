# !/usr/bin/env python3
#   testclsRecord.py - Testing Script for Church Database Records

import clsDB
import mysql

db = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
cn = ChurchDBConnection = mysql.connector.connect(**db.DB)
re = clsDB.clsRecord(cn, 'tblChurch', 'SELECT * FROM tblChurch')
print("current", re.get_current_record())
print("id = 1", re.get_record_by_id(1))
print("id = 2", re.get_record_by_id(2))
print("next", re.next_record())
print("prev", re.prev_record())
print("")
print("current", re.get_current_record())
re.RECORDS[re.CURRENTRECORD].update({'Church': 'New Church Name'})
print("current", re.get_current_record())
re.update_current_record()
print("current", re.get_current_record())
