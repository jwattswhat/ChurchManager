"""
    clsSQL - classes for handling SQL 
    Rev. Jonathan C. Watt
    August 1, 2022
"""


from mysql.connector import FieldType
import datetime

from clsConfig import CONFIG
from clsOption import OPTION


class clsSQL:
    class clsAsPairs:
        def __init__(self, sqlcolumns):
            self.find(sqlcolumns)

        def find(self, sqlcolumns):
            self._aspairs = {}
            for i in range(len(sqlcolumns)):
                s = sqlcolumns[i].find(" as ")
                if s != -1:
                    e = s + 4
                    first = sqlcolumns[i][:s]
                    last = sqlcolumns[i][e:]
                    self._aspairs.update({last: first})

        def getall(self, fieldlist):
            returnlist = []
            for i in range(len(fieldlist)):
                returnlist.append(self.get(fieldlist[i]))
            return returnlist

        def get(self, field):
            if field in self._aspairs:
                return self._aspairs[field]
            return field

    def __init__(self, dbconnection, table, parentrecord=None):
        self.dbconnection = dbconnection
        self.table = table
        self.parentrecord = parentrecord

        self.aspairs = self.clsAsPairs(self.table["fields"])
        self.sqldescription = self._build_sql_record_description()

    def select(self, tbl=None):
        if tbl == None:
            table = self.table.copy()
        else:
            table = tbl.copy()
        sql = ""
        if "name" in table:
            if table["fields"] == ["*"]:
                sql = "SELECT {fields} FROM {table} ".format(
                    fields=", ".join(table["fields"]),
                    table=table["name"],
                )
            else:
                sql = "SELECT {fields} FROM {table} ".format(
                    fields=", ".join(table["fields"]),
                    table=table["name"],
                )
        if "condition" in table:
            table["condition"] = self.conditionCONFIG(table["condition"])
            if self.parentrecord == None:
                sql = sql + "WHERE {condition} ".format(condition=table["condition"])
            else:
                sql = sql + "WHERE {condition} ".format(
                    condition=self.condition(table["condition"]),
                )
        if "orderby" in table:
            sql = sql + "ORDER BY {orderby}".format(orderby=table["orderby"])
        return sql

    def conditionCONFIG(self, condition):
        pos = 0
        while True:
            start = condition.find("{OPTION", pos)
            if start == -1:
                break
            end = condition.find("}", start)
            c1 = condition.find(":", start)
            c2 = condition.find(":", c1 + 1)
            optionvalue = condition[c1 + 1 : c2]
            optionfor = condition[c2 + 1 : end]
            pos = start
            condition = condition.replace(
                condition[start : end + 1],
                '"' + OPTION.get_Option_Value(optionfor, optionvalue) + '"',
                1,
            )
        return condition

    def condition(self, condition, parentrecord=None):
        if parentrecord == None:
            parentrecord = self.parentrecord.copy()

        start = True
        while start != -1:
            start = condition.find("{")
            if start != -1:
                end = condition.find("}")
                fieldname = condition[start + 1 : end]
                condition = condition.replace(
                    "{" + fieldname + "}", str(parentrecord[fieldname])
                )
        return condition

    def insert(self, record):
        ky, va = self._prepare_keys_values(record)

        keys = []
        values = []
        for k in range(len(va)):  # remove all fields with None.
            if va[k] != "":
                keys.append(ky[k])
                val = va[k].replace(
                    "\\", "\\\\"
                )  # replace all \\ with \\\\ for SQL Execute Statement.
                values.append(val)
        sql = "INSERT INTO {table} ({keys}) VALUES ({values});".format(
            table=self.table["name"], keys=", ".join(keys), values=", ".join(values)
        )
        return sql

    def update(self, record):
        keys, values = self._prepare_keys_values(record)
        valuestrings = []
        for k in range(len(keys)):
            value = values[k].replace(
                "\\", "\\\\"
            )  # replace all \\ with \\\\ for SQL Execute Statement.
            valuestrings.append("{key}={value}".format(key=keys[k], value=value))

        sql = "UPDATE {table} SET {values} WHERE ID={id};".format(
            table=self.table["name"],
            values=", ".join(valuestrings),
            id=record["ID"],
        )

        return sql

    def delete(self, recordID):
        return "DELETE FROM {tablename} WHERE ID = {ID};".format(
            tablename=self.table["name"], ID=recordID
        )

    def get_sql_field_description(self, field):
        return self.sqldescription[field]

    def get_sql_record_description(self):
        return self.sqldescription

    def format_by_sql_description(self, field, value):
        global CONFIG

        if (value == None) or (value == ""):
            return "NULL"
        match self.sqldescription[field]["type"]:
            case "TINY":
                return value == 1
            case "LONG":
                return value
            case "TIME":
                return value.strftime(CONFIG.get_Config_Value("Format", "Time"))
            case "DATE":
                return value.strftime(CONFIG.get_Config_Value("Format", "Date"))
            case "DATETIME":
                return value.strftime(CONFIG.get_Config_Value("Format", "DateTime"))
            case other:
                return value

    def format_sql_records(self, sqlrows):
        returnrecords = []
        for row in range(len(sqlrows)):
            record = {}
            for column, columnname in enumerate(list(self.sqldescription.keys())):
                field = sqlrows[row][column]
                if field == "":
                    field = None
                record.update({columnname: self._format_for_record(columnname, field)})
            returnrecords.append(record)
        return returnrecords

    def get_blank_record(self):
        global CONFIG

        record = {}
        for key in self.sqldescription:
            if self.sqldescription[key]["type"] == "TINY":  # Check for Boolean
                record.update({key: False})
            elif self.sqldescription[key]["type"] == "DATE":
                record.update({key: None})
            elif self.sqldescription[key]["type"] == "DATETIME":
                record.update({key: None})
            else:
                record.update({key: None})
        if record != {}:
            return record
        return None

    #   internal methods

    def _build_sql_record_description(self):
        sql = "SELECT {fields} FROM {table} LIMIT 1;".format(
            fields=",".join(self.table["fields"]), table=self.table["name"]
        )

        cursor = self.dbconnection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()

        recorddescription = {}
        for column in cursor.description:
            recorddescription.update(
                {
                    column[0]: {
                        "type": FieldType.get_info(column[1]),
                        "null_ok": (column[6] == 1),
                        "flags": column[7],
                    }
                }
            )
        cursor.close()
        return recorddescription

    def _prepare_keys_values(self, record):
        rec = record.copy()
        for d in rec.copy():
            if d == "ID":
                rec.pop("ID")
                continue
            rec[d] = self._format_with_description(d, rec[d])
        values = list(rec.values())

        keys = list(rec.keys())
        keys = self.aspairs.getall(keys)

        return keys, values

    def _string_to_list(self, st):
        stripit = ["[", "]", ","]
        if st[:1] != "[":
            return str(st)
        for s in stripit:
            st = st.replace(s, "")
        return st.splitlines()

    def _format_for_record(self, field, value):
        # print(self, field, value)
        if value == None:
            return None

        match self.sqldescription[field]["type"]:

            #   string types

            case "VAR_STRING":
                value = self._string_to_list(value)

            case "STRING":
                value = self._string_to_list(value)

            case "BLOB":
                value = self._string_to_list(value)

            #   Boolean types

            case "TINY":
                if value:
                    value = True
                else:
                    value = False

            #   Numeric
            case "FLOAT":
                value = value

            case "LONG":
                value = value

            #   Date and Time Types

            case "DATETIME":
                value = value.strftime(CONFIG.get_Config_Value("Format", "DateTime"))
            case "DATE":
                value = value.strftime(CONFIG.get_Config_Value("Format", "Date"))
            case "TIME":
                dt = datetime.datetime(2022, 1, 1) + value
                value = dt.strftime(CONFIG.get_Config_Value("Format", "Time"))

            #   Default to string type

            case other:
                value = '"' + str(value) + '"'

        # print (field," : ",self.sqldescription[field]["type"]," : ",value)
        return value

    def _list_to_string(self, li):
        if type(li) != list:
            return "'" + li + "'"
        for l in range(len(li)):
            li[l] = li[l].replace("'", "'")
            li[l] = li[l].replace('"', '"')
            li[l] = li[l].replace("'", "'")
            li[l] = li[l].replace('"', '"')
        return "'[" + "\r".join(li) + "]'"

    def _format_with_description(self, field, value):
        if value == None:
            return "Null"

        # print (field,value,self.sqldescription[field]["type"])
        match self.sqldescription[field]["type"]:
            #   String types
            case "VAR_STRING":
                value = self._list_to_string(value)

            case "STRING":
                value = self._list_to_string(value)

            case "BLOB":
                value = self._list_to_string(value)

            #   Boolean types

            case "TINY":
                if value:
                    value = "True"
                else:
                    value = "False"

            #   Numeric Types

            case "LONG":
                value = str(value)

            case "FLOAT":
                value = str(value)

            #   Date and Time Types

            case "DATETIME":
                value = "STR_TO_DATE('{date}','{dateformat}')".format(
                    date=value,
                    dateformat=CONFIG.get_Config_Value("SQLFormat", "DateTime"),
                )
            case "DATE":
                value = "STR_TO_DATE('{date}','{dateformat}')".format(
                    date=value, dateformat=CONFIG.get_Config_Value("SQLFormat", "Date")
                )

            case "TIME":
                value = "STR_TO_DATE('{time}','{dateformat}')".format(
                    time=value, dateformat=CONFIG.get_Config_Value("SQLFormat", "Time")
                )

            #   Default to string type

            case other:
                value = "'" + +str(value) + "'"

        return value
