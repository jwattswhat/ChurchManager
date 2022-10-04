def parse_sql_table(self.table):
    sql = ""
    if "name" in table:
        if table["fields"] == ["*"]:
            sql = "SELECT {fields} FROM {table} ".format(
                fields=",".join(table["fields"]),
                table=table["name"],
            )
        else:
            sql = "SELECT {fields} FROM {table} ".format(
                fields=",".join(table["fields"]),
                table=table["name"],
            )
    if "condition" in table:
        sql = sql + "WHERE {condition} ".format(
            condition=self.parse_sql_condition(table["condition"]),
        )
    if "orderby" in table:
        sql = sql + "ORDER BY {orderby}".format(orderby=table["orderby"])
    return sql

def find_aspairs(self,pairs):
    aspairs = {}
    for i in range(len(pairs)):
        s = pairs[i].find(" as ")
        if s != -1:
            e = s + 4
            first=pairs[i][:s]
            last=pairs[i][e:]
            aspairs.update({last:first})
    if aspairs == {}:
        return None
    return aspairs 

def parse_sql_condition(self,condition):
    start = True
    while start != -1:
        start = condition.find("{")
        if start != -1:
            end = condition.find("}")
            fieldname = condition[start + 1 : end]
            fld = self.get_field_by_name(fieldname)
            condition = condition.replace(
                "{" + fieldname + "}", str(self.get_field_by_name(fieldname))
            )
    return condition

table = {
    "name": "TestTable",
    "fields" : ["one","two as three","four","five as six"],
    "orderby" : "five"
}

print(parse_sql_table(table))