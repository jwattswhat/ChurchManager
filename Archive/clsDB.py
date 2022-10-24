"""
    clsDB.py - Church Database Classes
    Rev. Jonathan C. Watt
    July 1, 2021
"""

#   System Imports

import mysql
import mysql.connector
from mysql.connector import FieldType
from mysql.connector.errors import Error
from datetime import datetime, timedelta

#   Framework Imports

import clsSQL
from clsConfig import CONFIG
import clsError

class clsDB:
    """
    clsDB -
    Rev. Jonathan C. Watt
    July 2021

    DB = dictionary description of username, password, host, database
    DBconnection = connection to database
    """

    DBConnection = 0

    def __init__(self, host, databasename, username, password):
        self.DB = {
            "user": username,
            "password": password,
            "host": host,
            "database": databasename,
        }

    def connect(self):
        try:
            self.DBConnection = mysql.connector.connect(**self.DB)
        except mysql.connector.Error as e:
            raise clsError.clsErrorHandler(e.errno,e.msg)
            exit()
        else:
            self.DBConnection.close()


class clsRecord:
    """
    <TODO> Add comments for clsRecord
        clsRecord -
        Rev. Jonathan C. Watt
        July 2021
    """

    class clsOriginalRecord:
        def __init__(self):
            self.record = {}

        def saverecord(self, record):
            self.record = record.copy()
            for field in self.record:
                self.savefield(field, self.record[field])

        def savefield(self, field, value):
            if value == "":
                self.record[field] = None
            else:
                self.record[field] = value

        def getsavedfield(self, field):
            return self.record[field]

        def restore(self):
            return self.record

        def comparefield(self, field, value):
            return str(value) == str(self.record[field])

        def comparerecord(self, record):
            errorfields = []
            for field in record:
                if self.original[field] == "":
                    self.original[field] == None
                if record[field] == "":
                    record[field] = None
                # print (self.original[field],record[field],self.original[field]==record[field])
                if str(self.original[field]) != str(record[field]):
                    errorfields.append(field)
            if errorfields != []:
                return errorfields
            return False

    def __init__(self, connection, table=None):
        """
        DBConnection - connection to database
        TABLE - dictionary containing table info
            "table" : {
                "name" : "TableName",
                "fields" : ["fieldname","fieldname"],
                "condition" : "SQLWhere Clause",
                "orderby" : "SQLOrderClause"
            }
        ...
        """
        self.DBConnection = connection
        self.TABLENAME = table["name"]
        self.original = self.clsOriginalRecord()
        self.TABLE = table
        self._record = None
        self._position = 0
        self.sqlaspairs = None

    def load_records(self, table=None, parentrecord=None):
        if table == None:
            table = self.TABLE
        self._record = self.read_records(table, parentrecord)
        if not self._record:
            self.add(self.sql.get_blank_record())
            return "NewRecord"
        self.first()

    def read_records(self, table=None, parentrecord=None):
        global CONFIG

        self.sql = clsSQL.clsSQL(self.DBConnection, table, parentrecord)
        cursor = self.DBConnection.cursor()
        sql = self.sql.select()
        try:
            cursor.execute(sql)
        except mysql.connector.Error as e:
            raise clsError.clsErrorHandler(e.errno,e.msg)
            return None
        rows = cursor.fetchall()
        if len(rows) == 0:
            return []

        records = self.sql.format_sql_records(rows)
        if records != []:
            return records
        return []

    def add(self, rec):
        if self.isempty():
            self._record = []
        self._record.append(rec)
        return self.last()

    def delete(self):
        if not self.isempty():
            self._record.pop(self._position)
            self.prev()

    def current(self):
        if not self.isempty():
            return self._record[self._position]

    def currentfield(self, field):
        return self._record[self._position][field]

    def currentnum(self):
        return self._position

    def first(self):
        if not self.isempty():
            self._position = 0
            self.original.saverecord(self._record[self._position])
            return self._record[self._position]

    def prev(self):
        if self._position > 0:
            self._position -= 1
        self.original.saverecord(self._record[self._position])
        return self._record[self._position]

    def next(self):
        if self._position < len(self._record) - 1:
            self._position += 1
            self.original.saverecord(self._record[self._position])
            return self._record[self._position]

    def last(self):
        self._position = len(self._record) - 1
        self.original.saverecord(self._record[self._position])
        return self._record[self._position]

    def setfieldvalue(self, field, value):
        self._record[self._position][field] = value

    def updatecurrentrec(self, rec):
        self._record[self._position] = rec

    def getcurrentID(self):
        if not self.isempty():
            return self._record[self._position]["ID"]

    def getfield(self, name):
        return self._record[self._position][name]

    def setControlID(self, name, ID):
        self._record[self._position][name].update({"ControlID": ID})

    def ControlID(self):
        return self._record[self._position]["ControlID"]

    def get_field_by_name(self, fieldname):
        return self._record[self._position].get(fieldname)

    def isempty(self):
        return self._record == None

    def fieldisdirty(self, field):
        return str(self.original.record[field]) != str(
            self._record[self._position][field]
        )

    def recordisdirty(self):
        dirtyfields = []
        for field in self._record[self._position]:
            if self.fieldisdirty(field):
                dirtyfields.append(field)
        return dirtyfields

    #
    #   internal methods
    #

    def delete_record_from_DB(self):
        """
        delete record from the DB
        """
        cursor = self.DBConnection.cursor()
        sql = self.sql.delete(self._record[self._position]["ID"])
        try:
            cursor.execute(sql)
        except mysql.connector.Error as e:
            raise clsError.clsErrorHandler(e.errno,e.msg)
        self.DBConnection.commit()

        # delete record from the dictionary
        self.delete()

    def update_current_record_in_DB(self):

        # Insert New Record "ID" Field is None
        if self._record[self._position]["ID"] == None:
            cursor = self.DBConnection.cursor()
            sql = self.sql.insert(self._record[self._position])
            try:
                cursor.execute(sql)
            except mysql.connector.Error as e:
                raise clsError.clsErrorHandler(e.errno,e.msg)
            self.DBConnection.commit()

            # Get the ID (autoincrement field) from the last Insert
            sql = "SELECT Last_Insert_ID();"
            try:
                cursor.execute(sql)
            except mysql.connector.Error as e:
                raise clsError.clsErrorHandler(e.errno,e.msg)
            lid = cursor.fetchone()
            cursor.close()
            self.setfieldvalue("ID", lid[0])

        # Update existing record only update fields that have changed.
        else:
            cursor = self.DBConnection.cursor()
            sql = self.sql.update(self._record[self._position])
            try:
                cursor.execute(sql)
            except mysql.connector.Error as e:
                raise clsError.clsErrorHandler(e.errno,e.msg)
            self.DBConnection.commit()
            cursor.close()
        self.original.saverecord(self.current())

    def __close__(self):
        if self.DBConnection.isconnected():
            self.DBConnection.close()
