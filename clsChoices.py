import clsSQL


class clsChoices:
    """
    clsChoiceList

    This class is used to manage dropdown lists for ComboBoxes.
        display - list of dropdown display values
        fieldname - list of fieldnames in the display value
        fielddata - list of the data related to the fieldname (seperated for easy use)
    """

    def __init__(self, dbconnection, controldescription):

        self.dbconnection = dbconnection
        self.controldescription = controldescription

        self.id = []
        self.fieldname = self.controldescription["name"]  # list of the fieldnames
        self.display = []  # list of dropdown display values

        self.fielddata = []  # list of fielddata

    def Load_Choices(self, controldescription):
        if controldescription != None:
            controldescription = self.controldescription

        if "choices" in controldescription:
            return controldescription["choices"]

        self.choiceslist = None
        self.subfields = []
        choices = None
        choices = self._loadfromchoicestable()
        if choices == None:
            choices = self._loadchoicesfromtable()
        return choices

    def _loadfromchoicestable(self):
        """
        this module looks for field choices for 'fieldname' in the tblChoices table
        Choices are loaded automaticlly based on the field name.
        Return None if no choices are found.
        """
        choicesSQL = "SELECT Choices FROM tblChoices WHERE field='{fieldname}';".format(
            fieldname=self.fieldname
        )
        cursor = self.dbconnection.cursor()
        cursor.execute(choicesSQL)
        row = cursor.fetchone()
        cursor.close()
        choices = None
        if row != None:
            choices = row[0].replace("[", "")
            choices = choices.replace("]", "")
            choices = choices.replace(",", "")
            choices = choices.splitlines()
        return choices

    def _loadchoicesfromtable(self):
        """
        this routine loads the field choice list when it is in another table. It is used to replace the "choices" parameter
        for wxPython calls.

        JSON values

        "lookupchoices" :{
            "name": "tblXXXX",                 # table to use for lookup
            "fields: ["fieldname","fieldname"]   # Display fields
            "orderby" : "sortfield"                # field to sort lookup
        """
        if "lookupchoices" not in self.controldescription:
            return None

        self.sql = clsSQL.clsSQL(
            self.dbconnection, self.controldescription["lookupchoices"]
        )
        SQL = self.sql.select()
        cursor = self.dbconnection.cursor()
        cursor.execute(SQL)
        rows = cursor.fetchall()
        cursor.close()

        choice = []
        for row in rows:
            combinevalues = ""
            fields = []
            for column in range(1, len(row)):
                # fld = sql.format_by_sql_description(column,row[column])
                combinevalues = combinevalues + str(row[column]) + " "
                fields.append(row[column])
                self.subfields.append(row[column])
            choice.append(combinevalues.strip())
            self._addchoiceanddata(row[0], combinevalues, fields)

        return self.display

    def _addchoiceanddata(self, id, display, fielddata):
        self.id.append(id)
        self.display.append(display)
        self.fielddata.append(fielddata)

    def getchoiceid(self, display):
        if display not in self.display:
            return display

        for i in range(len(self.display)):
            if self.display[i] == display:
                return self.id[i]
        return None

    def getchoicedisplay(self, id):
        if id not in self.id:
            return id

        for i in range(len(self.id)):
            if self.id[i] == id:
                return self.display[i]
        return None

    def len(self):
        return len(self.display)
