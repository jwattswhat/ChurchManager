class clsConfig:
    """
    clsConfig.py - Configuration Class for getting and setting system configuration
    Rev. Jonathan C. Watt
    July 2022
    """

    DBConnection = None

    def __init__(self, DBConnection=None):
        self.DBConnection = DBConnection

    def set_Config_DBConnection(self, DBConnection):
        self.DBConnection = DBConnection

    def get_Config_Value(self, ConfigFamily, ConfigType):
        if self.DBConnection == None:
            return None
        SQL = "SELECT ConfigValue FROM tblConfig WHERE ConfigFamily = '{ConfigFamily}' AND ConfigType = '{ConfigType}';".format(
            ConfigFamily=ConfigFamily, ConfigType=ConfigType
        )
        cursor = self.DBConnection.cursor()
        cursor.execute(SQL)
        row = cursor.fetchone()
        cursor.close()
        return row[0]

    def set_Config_Value(self, ConfigFamily, ConfigType, ConfigValue):
        if self.DBConnection == None:
            return None
        SQL = "UPDATE tblConfig SET ConfigFamily = '{ConfigFamily}', ConfigValue = '{ConfigValue}' WHERE ConfigType = '{ConfigType}';".format(
            ConfigValue=ConfigValue, ConfigType=ConfigType
        )
        cursor = self.DBConnection.cursor()
        cursor.execute(SQL)
        cursor.close()

    def get_Config_Family(self, configfamily):
        if self.DBConnection == None:
            return None
        SQL = "SELECT ConfigType, ConfigValue FROM tblConfig WHERE ConfigFamily = '{configfamily}';".format(
            configfamily=configfamily
        )
        cursor = self.DBConnection.cursor()
        cursor.execute(SQL)
        rows = cursor.fetchall()
        cursor.close()
        return rows


CONFIG = clsConfig()
