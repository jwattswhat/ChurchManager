class clsOption:
    """
    clsOption.py - Option Class for Getting and Setting System Options
    Rev. Jonathan C. Watt
    August 9, 2022
    """

    DBConnection = None

    def __init__(self, DBConnection=None):
        self.DBConnection = DBConnection

    def set_Option_DBConnection(self, DBConnection):
        self.DBConnection = DBConnection

    def get_Option_Value(self, optionfor, optiontype):
        if self.DBConnection == None:
            return None
        SQL = 'SELECT OptionValue FROM tblOptions WHERE OptionFor = "{optionfor}" AND OptionType = "{optiontype}";'.format(
            optionfor=optionfor, optiontype=optiontype
        )
        cursor = self.DBConnection.cursor()
        cursor.execute(SQL)
        row = cursor.fetchone()
        cursor.close()
        return row[0]

    def set_Option_Value(self, optionfor, optiontype, optionvalue):
        if self.DBConnection == None:
            return None
        SQL = "UPDATE tblOption SET OptionValue ='{OptionValue}' WHERE OptionFor = '{OptionFor}' AND OptionValue='{OptionValue}';".format(
            OptionFor=optionfor, OptionType=optiontype, OptionValue=optionvalue
        )
        cursor = self.DBConnection.cursor()
        cursor.execute(SQL)
        cursor.close()


OPTION = clsOption()
