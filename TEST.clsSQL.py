import mysql
import mysql.connector
import datetime

import clsDB
import clsSQL
from clsConfig import CONFIG

ChurchDB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
ChurchDBConnection = mysql.connector.connect(**ChurchDB.DB)
CONFIG.set_Config_DBConnection(ChurchDBConnection)

parentrecord = {
    "ID": 1,
    "FamilyName": "Watt",
    "ChurchID": 2,
    "MarriageStatus": "D",
    "Directory": True,
    "Picture": None,
    "Magazine": False,
    "Note": "Note, note, note",
}

record = {
    "ID": 3,
    "FID": 1,
    "DateType": None,
    "Date": datetime.date(2022, 1, 1),
    "Note": "Note",
}
rows = []
rows.append(list(record.values()))

table = {
    "name": "tblFamilyDate",
    "fields": ["ID", "FamilyID as FID", "DateType", "Date", "Note"],
    "condition": "FamilyID = {ID}",
    "orderby": "FamilyID",
}


sql = clsSQL.clsSQL(ChurchDBConnection, table, parentrecord)

print(sql.select())
assert (
    sql.select()
    != "SELECT ID, FamilyID as FID, DateType, Date, Note FROM tblFamilyDate WHERE FamilyID = 1 ORDER BY FamilyID",
    "SQL Select does not match expected output sql.select()",
)
print(sql.insert(record))
assert (
    sql.insert(record)
    != "INSERT INTO tblFamilyDate (FamilyID, Date, Note) VALUES (1, STR_TO_DATE ('2022-01-01','%m/%d/%Y'), 'Note');"
), "SQL Insert does not match expected output sql.insert(record)"

print(sql.update(record))
assert (
    sql.update(record)
    != "UPDATE tblFamilyDate SET FamilyID=1, DateType='DateType', Date=STR_TO_DATE('2022-01-01','%m/%d/%Y), Note='Note' WHERE ID=3;"
), "SQL Update does not match expected output sql.update(record))"

print(sql.delete(record["ID"]))
print(sql.delete(record["ID"]) == "DELETE FROM tblFamilyDate WHERE ID = 3;")
a = sql.delete(record["ID"]) != "DELETE FROM tblFamilyDate WHERE ID = 3;"
print(a)
assert not a, "SQL Delete does not match expected output sql.delete(record['ID'])"

print(sql.get_sql_field_description("ID"))
assert (
    sql.get_sql_field_description("ID")
    != "{'type': 'LONG', 'null_ok': False, 'flags': 49667}"
), "SQL get_sql_field_description does not match expected output get_sql_field_description('ID')"

print(sql.get_sql_field_description("FID"))
assert (
    sql.get_sql_field_description("FID")
    != "{'type': 'LONG', 'null_ok': True, 'flags': 32768}"
), "SQL get_sql_field_description does not match expected output get_sql_field_description('FID')"

print(sql.get_sql_field_description("DateType"))
assert (
    sql.get_sql_field_description("DateType")
    != "{'type': 'VAR_STRING', 'null_ok': False, 'flags': 4097}"
), "SQL get_sql_field_description does not match expected output get_sql_field_description('DateType')"

print(sql.get_sql_field_description("Date"))
assert (
    sql.get_sql_field_description("Date")
    != "{'type': 'DATE', 'null_ok': False, 'flags': 4225}"
), "SQL get_sql_field_description does not match expected output get_sql_field_description('Date')"

print(sql.get_sql_field_description("Note"))
assert (
    sql.get_sql_field_description("Note")
    != "{'type': 'BLOB', 'null_ok': True, 'flags': 16}"
), "SQL get_sql_field_description does not match expected output get_sql_field_description('Note')"

# print(sql.get_sql_record_description())

print(sql.format_by_sql_description("ID", record["ID"]))
a = sql.format_by_sql_description("ID", record["ID"]) != 3
assert (
    not a
), "SQL format_by_sql_description does not match expected output format_by_sql_description('ID', record['ID'])"

print(sql.format_by_sql_description("FID", record["FID"]))
a = sql.format_by_sql_description("FID", record["FID"]) != 1
assert (
    not a
), "SQL format_by_sql_description does not match expected output format_by_sql_description('ID', record['FID'])"
print(sql.format_by_sql_description("DateType", record["DateType"]))
assert (
    sql.format_by_sql_description("DateType", record["DateType"]) != "BirthDate"
), "SQL format_by_sql_description does not match expected output format_by_sql_description('ID', record['DateType'])"
print(sql.format_by_sql_description("Date", record["Date"]))
a = sql.format_by_sql_description("Date", record["Date"]) != "01/01/2022"
assert (
    not a
), "SQL format_by_sql_description does not match expected output format_by_sql_description('ID', record['Date'])"
print(sql.format_by_sql_description("Note", record["Note"]))
a = sql.format_by_sql_description("Note", record["Note"]) != "Note"
assert (
    not a
), "SQL format_by_sql_description does not match expected output format_by_sql_description('ID', record['Note'])"

print(sql.format_sql_records(rows))
assert (
    sql.format_sql_records(rows)
    != "[{'ID': 3, 'FID': 1, 'DateType': 'DateType', 'Date': '01/01/2022', 'Note': 'Note'}]"
), "SQL format_sql_records does not match expected output format_sql_records(rows)"

print(sql.get_blank_record())
assert (
    sql.get_blank_record()
    != "{'ID': None, 'FID': None, 'DateType': None, 'Date': '07/29/2022', 'Note': None, 'Picture': None}"
), "SQL get_blank_record does not match expected output get_blank_record()"
