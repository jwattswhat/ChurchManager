"""
    checkforms.py
    check all forms for valid format using JSONSchema
    Rev. Jonathan C. Watt
    April 7, 2023
"""
import JSForm

from jsonschema import validate
import pathlib
import argparse
import json

cmparser = argparse.ArgumentParser(
    prog="ChurchManager",
    description="Church Manager v0.1"
)
cmparser.add_argument("-s","--server",type=str,default="localhost")
cmparser.add_argument("-d","--database",type=str,default="ChurchDB")
cmparser.add_argument("-u","--user",type=str)
cmparser.add_argument("-p","--password",type=str)

args = cmparser.parse_args()

server = args.server
database = args.database
user = args.user
password = args.password

ChurchDB = JSForm.clsDB(server,database,user,password)
JSForm.CONFIG.set_Config_DBConnection(ChurchDB.DBConnection)

SchemaLocation = JSForm.CONFIG.get_Config_Value("Location","JSONSchema")
jsonschema = SchemaLocation + "jsformschema.json"
f = open(jsonschema)
schema = json.load(f)

FormLocation = JSForm.CONFIG.get_Config_Value("Location", "Form")

forms = pathlib.Path(JSForm.CONFIG.get_Config_Value("Location","Form"))
match input("Process all? (Y/N) "):
    case "Y"|"y":
        fn = None
    case _:
        fn = input("Enter Formname: ")

processform = None
for form in  forms.iterdir():
    if form.suffix == ".json":
        if fn and (form.stem != fn):
            continue
        formname = FormLocation + form.name
        f = open(
            formname,
        )
        jsonfrm = json.load(f)
        if processform != "All":
            processform = input("process forname {formname} (Y/N/All)? ".format(formname=formname))
        match processform:
            case "Y"|"y"|"Yes"|"All":
                print("checking {formname}".format(formname=formname))
                validate(instance=jsonfrm,schema=schema)
            case _:
                print ("bypassing {formname}".format(formname=formname))