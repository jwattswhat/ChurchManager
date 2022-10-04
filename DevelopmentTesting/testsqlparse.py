table = {
        "name": "tblReading",
        "fields": ["Reading", "Reference", "Note"],
        "condition": "Propers={ID} and B={Another}",
}
fieldvalue = "123456"

def parse_table(self,table):
    sql = "SELECT {fields} FROM {table} ".format(
        fields=",".join(table["fields"]),
        table=table["name"],
    )
    if "condition" in table:
        condition = table["condition"]
        start = True
        while start != -1:
            start = condition.find("{")
            if start != -1:
                end = condition.find("}")
                fieldname = "{"+condition[start + 1 : end]+"}"
                condition = condition.replace(fieldname, self.RECORDS.get_field_by_name(fieldname))
        sql = sql + "WHERE {condition} ".format(
                condition=condition,
            )
    if "order" in table:
        sql = sql + "ORDER BY {orderby}".format(orderby=table["orderby"])
    return sql


print(parse_table(table))

