import os
import json
from turtle import position
import mysql

from clsConfig import CONFIG
import clsDB

CHECKPOSITION = {
    "pos": {
        "vartype": "<class 'list'>",
        "requried": True,
    },
    "posch": {
        "vartype": "<class 'list'>",
        "requried": True,
    },
}

CHECKSIZE = {
    "size": {
        "vartype": "<class 'list'>",
        "requried": True,
    },
    "sizech": {
        "vartype": "<class 'list'>",
        "requried": True,
    },
}

CHECKTABLE = {
    "name": {
        "vartype": "<class 'str'>",
        "required": True,
        "values": "valid table name",
    },
    "fields": {
        "vartype": "<class 'list'>",
        "required": True,
        "values": "valid table columns",
    },
    "condition": {
        "vartype": "<class 'str'>",
        "required": False,
        "values": "SQL Condition",
    },
    "orderby": {
        "vartype": "<class 'str'>",
        "required": False,
        "values": "SQL orderby",
    },
}

CHECKFORM = {
    "type": {
        "vartype": "<class 'str'>",
        "required": True,
        "values": ["Panel", "Dialog", "StaticBox"],
    },
    "name": {
        "vartype": "<class 'str'>",
        "required": True,
    },
    "title": {"vartype": "<class 'str'>", "required": True},
    "pos": {},
    "size": {},
    "posch": {},
    "sizech": {},
    "table": {},
    "stylelist": {
        "vartype": "<class 'list'>",
        "required": True,
        "values": ["CAPTION", "MINIMIZEBOX", "MAXIMIZEBOX", "CLOSEBOX", "READONLY"],
    },
    "controls": {
        "vartype": "<class 'list'>",
        "required": True,
        "values": ["Navigation", "Update", "Close"],
    },
    # "linkedform": FORM,
    # "subform": FORM,
}

CHECKSTDCONTROLS = {
    "type": {
        "vartype": "<class 'str'>",
        "required": True,
        "values": [
            "StaticBox",
            "StaticText",
            "TextCtrl",
            "MultiLine",
            "ComboBox",
            "CheckBox",
            "CheckListBox",
            "Button",
            "DataViewListCtrl",
            "DateTime",
            "DatePickerCtrl",
            "TimePickerCtrl",
            "CalendarCtrl",
            "FilePickerCtrl",
        ],
    },
    "name": {
        "vartype": "<class 'str'>",
        "required": True,
    },
    "pos": {},
    "posch": {},
    "table": {},
    "stylelist": {
        "vartype": "<class 'list'>",
        "required": True,
        "values": [
            "MULTILINE",
            "DONTWRAP",
            "WORDWRAP",
            "PROCESSENTER",
            "PROCESSTAB",
            "READONLY",
        ],
    },
}

CHECKNAMEDCONTROLS = {
    "StaticBox": {
        "label": {"vartype": "<class 'str'>", "required": True},
        "size": {},
        "sizech": {},
    },
    "StaticText": {"label": {"vartype": "<class 'str'>", "required": True}},
    "TextCtrl": {
        "value": {"vartype": "<class 'str'>", "required": True},
        "size": {},
        "sizech": {},
        "lookupchoices": {},
    },
    "MultiLine": {
        "size": {},
        "sizech": {},
    },
    "ComboBox": {
        "value": {"vartype": "<class 'str'>", "required": True},
        "size": {},
        "sizech": {},
        "choices": {},
        "refreshform": {"vartype": "<class 'boolean'>", "required": False},
    },
    "CheckBox": {
        "value": {"vartype": "<class 'str'>", "required": True},
        "size": {},
        "sizech": {},
    },
    "CheckListBox": {
        "label": {"vartype": "<class 'str'>", "required": True},
        "size": {},
        "sizech": {},
        "choices": {},
    },
    "Button": {
        "id": {"vartype": "<class 'int'>", "required": True},
        "label": {"vartype": "<class 'str'>", "required": True},
        "size": {},
        "sizech": {},
        "open": {},
    },
    "DataViewListCtrl": {
        "position": {},
        "size": {},
        "sizech": {},
        "table": CHECKTABLE,
        "columns": {},
    },
    "DateTime": {"id": {}, "size": {}, "sizech": {}, "dt": {}},
    "DatePickerCtrl": {"id": {}, "size": {}, "sizech": {}, "dt": {}},
    "TimePickerCtrl": {
        "size": {},
        "sizech": {},
    },
    "CalendarCtrl": {
        "size": {},
        "sizech": {},
    },
    "FilePickerCtrl": {
        "size": {},
        "sizech": {},
    },
}


def load_form_from_json(Form):
    """
    loads form description from a JSON file.
    """
    global CONFIG

    FormLocation = CONFIG.get_Config_Value("Location", "Form")

    formname = FormLocation + Form + ".json"
    f = open(
        formname,
    )
    jsonfrm = json.load(f)
    return jsonfrm[Form + "FORM"]["FORM"], jsonfrm[Form + "FORM"]["CONTROLS"]


def checkposition(formname, tablename, tocheck):
    passed = True
    if ("pos" in tocheck) and ("posch" in tocheck):
        printmessage(
            ew="WARNING:",
            form=formname,
            table=tablename,
            field="pos",
            message="'pos' overrides 'posch'",
        )
    if ("size" in tocheck) and ("sizech" in tocheck):
        printmessage(
            ew="WARNING:",
            form=formname,
            table=tablename,
            field="pos",
            message="'size' overrides 'sizech'",
        )

    if ("pos" in tocheck) and ("size" not in tocheck):
        printmessage(
            form=formname,
            table=tablename,
            field="size",
            message="'pos' and 'size' must both be present",
        )
        passed = False
    if ("pos" not in tocheck) and ("size" in tocheck):
        printmessage(
            form=formname,
            table=tablename,
            field="pos",
            message="'pos' and 'size' must both be present",
        )
        passed = False
    if ("posch" in tocheck) and ("sizech" not in tocheck):
        printmessage(
            form=formname,
            table=tablename,
            field="sizech",
            message="'posch' and 'sizech' must both be present",
        )
        passed = False
    if ("posch" not in tocheck) and ("sizech" in tocheck):
        printmessage(
            form=formname,
            table=tablename,
            field="posch",
            message="'posch' and 'sizech' must both be present",
        )
        passed = False

    for checkfield in CHECKPOSITION:
        if checkfield not in tocheck:
            continue
        if type(tocheck[checkfield]) != list:
            printmessage(
                form=formname,
                table=tablename,
                field=checkfield,
                data=tocheck[checkfield],
                message=" must be an a list of 2 integers",
            )
            passed = False
            continue
        if len(tocheck[checkfield]) > 2:
            printmessage(
                form=formname,
                table=tablename,
                field=checkfield,
                data=tocheck[checkfield],
                message=" must be an a list of 2 integers",
            )
            passed = False
        if type(tocheck[checkfield][0]) != int:
            printmessage(
                form=formname,
                table=tablename,
                field=checkfield + "[0]",
                data=tocheck[checkfield][0],
                message=" must be an integer",
            )
            passed = False
        if type(tocheck[checkfield][1]) != int:
            printmessage(
                form=formname,
                table=tablename,
                field=checkfield + "[1]",
                data=tocheck[checkfield][1],
                message=" must be an integer",
            )
            passed = False

    return passed


def checksize(formname, tablename, tocheck):
    passed = True
    if ("size" in tocheck) and ("sizech" in tocheck):
        printmessage(
            ew="WARNING:",
            form=formname,
            table=tablename,
            field="pos",
            message="'size' overrides 'sizech'",
        )
    for checkfield in CHECKSIZE:
        if checkfield not in tocheck:
            continue
        if type(tocheck[checkfield]) != list:
            printmessage(
                form=formname,
                table=tablename,
                field=checkfield,
                data=tocheck[checkfield],
                message=" must be an a list of 2 integers",
            )
            passed = False
            continue
        if len(tocheck[checkfield]) > 2:
            printmessage(
                form=formname,
                table=tablename,
                field=checkfield,
                data=tocheck[checkfield],
                message=" must be an a list of 2 integers",
            )
            passed = False
        if type(tocheck[checkfield][0]) != int:
            printmessage(
                form=formname,
                table=tablename,
                field=checkfield + "[0]",
                data=tocheck[checkfield][0],
                message=" must be an integer",
            )
            passed = False
        if type(tocheck[checkfield][1]) != int:
            printmessage(
                form=formname,
                table=tablename,
                field=checkfield + "[1]",
                data=tocheck[checkfield][1],
                message=" must be an integer",
            )
            passed = False

    return passed


def checktable(formname, tablename, tocheck):
    passed = True
    for checkfield in tocheck:
        if checkfield not in CHECKTABLE:
            printmessage(
                "WARNING:",
                form=formname,
                table=tablename,
                field=checkfield,
                message="field not found, ignored",
            )
            continue
        tabledata = tocheck.get(checkfield, None)
        if tabledata == None and CHECKTABLE[checkfield]["required"] == True:
            printmessage(
                formn=formname,
                table=tablename,
                field=checkfield,
                data=tabledata,
                message=" required, not found",
            )
            passed = False
            continue

        if checkfield in tocheck:
            if str(type(tocheck[checkfield])) != CHECKTABLE[checkfield]["vartype"]:
                printmessage(
                    form=formname,
                    table=tablename,
                    field=checkfield,
                    data=tabledata,
                    message=" invalid data type ",
                    moredata=str(type(tabledata)),
                )
                passed = False

        return passed
        cursor = DBConnection.cursor()
        match checkfield:
            case "name":
                sql = "SELECT * FROM {formname} LIMIT 1;".format(formname=formname)
                try:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                except Exception as ex:
                    passed = False
                    printmessage(
                        form=formname, table=tablename, message="table, not found"
                    )

            case "fields":
                for fd in tabletocheck["fields"]:
                    sql = "SELECT {field} FROM {tablename} LIMIT 1;".format(
                        field=fd, tablename=tablename
                    )
                    try:
                        cursor.execute(sql)
                        row = cursor.fetchone()
                    except Exception as ex:
                        passed = False
                        printmessage(
                            form=formname,
                            table=tablename,
                            field=fd,
                            message="field, not found",
                        )

            case "condition":
                if "condition" in tabletocheck:
                    sql = "SELECT * FROM {tablename} WHERE {condition} LIMIT 1;".format(
                        tablename=tablename, condition=tabletocheck["condition"]
                    )
                    try:
                        cursor.execute(sql)
                        row = cursor.fetchone()
                    except Exception as ex:
                        passed = False
                        printmessage(
                            form=formname,
                            table=tablename,
                            field=checkfield,
                            data=tabletocheck["condition"],
                            message=" invalid condition",
                        )
            case "orderby":
                if "orderby" in tabletocheck:
                    sql = "SELECT * FROM {formname} ORDER BY {orderby} LIMIT 1;".format(
                        formname=formname, orderby=tabletocheck["orderby"]
                    )
                    try:
                        cursor.execute(sql)
                        row = cursor.fetchone()
                    except Exception as ex:
                        passed = False
                        printmessage(
                            form=formname,
                            table=tablename,
                            field=checkfield,
                            data=tabletocheck["orderby"],
                            message=" invalid sort statment (orderby)",
                        )
    return passed


def checkform(formname, tocheck):
    passed = True
    positionchecked = False
    sizechecked = False
    for checkfield in tocheck:

        match checkfield:
            case "pos" | "posch":
                if not positionchecked:
                    passed = checkposition(formname, formname, tocheck)
                    positionchecked = True
                continue

            case "size" | "sizech":
                if not sizechecked:
                    passed = checksize(formname, formname, tocheck)
                    sizechecked = True
                continue

            case "table":
                passed = checktable(formname, formname, tocheck["table"])
                continue

        if checkfield not in CHECKFORM:
            printmessage(
                "WARNING:",
                form=formname,
                field=checkfield,
                message="field not found, ignored",
            )
            continue

        formdata = tocheck.get(checkfield, None)
        if (formdata == None) and (CHECKFORM[checkfield]["required"] == True):
            printmessage(
                form=formname,
                field=checkfield,
                data=formdata,
                message=" - required, not found",
            )
            passed = False
            continue

        if CHECKFORM[checkfield]["vartype"] != str(type(formdata)):
            printmessage(
                form=formname,
                field=checkfield,
                data=formdata,
                message=" invalid type ",
                moredata=str(type(formdata)),
            )
            passed = False
            continue

        if type(formdata) == str:
            formdata = formdata.split()
        for fd in formdata:
            if "values" in CHECKFORM[checkfield]:
                if fd not in CHECKFORM[checkfield]["values"]:
                    printmessage(
                        form=formname,
                        field=checkfield,
                        data=fd,
                        message=" not valid value must be in ",
                        moredata=str(CHECKFORM[checkfield]["values"]),
                    )
                    passed = False

    return passed


def checkstdcontrols(formname, controlname, tocheck):
    passed = True
    positionchecked = False

    if controlname not in CHECKNAMEDCONTROLS:
        printmessage(
            "WARNING:",
            form=formname,
            field=controlname,
            message="control not found, ignored",
        )
        return passed

    for checkfield in tocheck:
        if checkfield not in CHECKNAMEDCONTROLS[controlname]:
            match checkfield:
                case "pos" | "size" | "posch" | "sizech":
                    if not positionchecked:
                        passed = checkposition(formname, formname, tocheck)
                        positionchecked = True
                    continue

                case "table":
                    passed = checktable(formname, formname, tocheck["table"])
                    continue

            if checkfield not in CHECKSTDCONTROLS:
                printmessage(
                    "WARNING:",
                    form=formname,
                    field=checkfield,
                    message="field not found, ignored",
                )
                continue

            formdata = tocheck.get(checkfield, None)
            if (formdata == None) and (
                CHECKSTDCONTROLS[checkfield]["required"] == True
            ):
                printmessage(
                    form=formname,
                    field=checkfield,
                    data=formdata,
                    message=" - required, not found",
                )
                passed = False
                continue

            if CHECKSTDCONTROLS[checkfield]["vartype"] != str(type(formdata)):
                printmessage(
                    form=formname,
                    field=checkfield,
                    data=formdata,
                    message=" invalid type ",
                    moredata=str(type(formdata)),
                )
                passed = False
                continue

            if type(formdata) == str:
                formdata = formdata.split()
            for fd in formdata:
                if "values" in CHECKSTDCONTROLS[checkfield]:
                    if fd not in CHECKSTDCONTROLS[checkfield]["values"]:
                        printmessage(
                            form=formname,
                            field=checkfield,
                            data=fd,
                            message=" not valid value must be in ",
                            moredata=str(CHECKSTDCONTROLS[checkfield]["values"]),
                        )
                        passed = False

    return passed


def checknamedcontrol(formname, controlname, tocheck):

    passed = True
    positionchecked = False
    sizechecked = False
    if controlname not in CHECKNAMEDCONTROLS:
        printmessage(
            "WARNING:",
            form=formname,
            field=controlname,
            message="control not found, ignored",
        )
        return passed

    for checkfield in tocheck:
        if checkfield not in CHECKSTDCONTROLS:

            match checkfield:
                case "pos" | "posch":
                    if not positionchecked:
                        passed = checkposition(formname, formname, tocheck)
                        positionchecked = True
                    continue

                case "size" | "sizech":
                    if not sizechecked:
                        passed = checkposition(formname, formname, tocheck)
                        sizechecked = True
                    continue

                case "table":
                    passed = checktable(formname, formname, tocheck["table"])
                    continue

            if checkfield not in CHECKNAMEDCONTROLS[controlname]:
                printmessage(
                    "WARNING:",
                    form=formname,
                    field=checkfield,
                    message="field not found, ignored",
                )
                continue

            formdata = tocheck.get(checkfield, None)
            if (formdata == None) and (
                CHECKNAMEDCONTROLS[controlname][checkfield]["required"] == True
            ):
                printmessage(
                    form=formname,
                    field=checkfield,
                    data=formdata,
                    message=" - required, not found",
                )
                passed = False
                continue

            if (formdata == None) and (
                CHECKNAMEDCONTROLS[controlname][checkfield]["required"] == True
            ):
                printmessage(
                    form=formname,
                    field=checkfield,
                    data=formdata,
                    message=" - required, not found",
                )
                passed = False
                continue

            if CHECKNAMEDCONTROLS[controlname][checkfield]["vartype"] != str(
                type(formdata)
            ):
                printmessage(
                    form=formname,
                    field=checkfield,
                    data=formdata,
                    message=" invalid type ",
                    moredata=str(type(formdata)),
                )
                passed = False
                continue

            if type(formdata) == str:
                formdata = formdata.split()
            for fd in formdata:
                if "values" in CHECKNAMEDCONTROLS[controlname][checkfield]:
                    if fd not in CHECKNAMEDCONTROLS[controlname][checkfield]["values"]:
                        printmessage(
                            form=formname,
                            field=checkfield,
                            data=fd,
                            message=" not valid value must be in ",
                            moredata=str(
                                CHECKNAMEDCONTROLS[controlname][checkfield]["values"]
                            ),
                        )
                        passed = False

    return passed


def checkcontrol(formname, controlname, control):
    passed = True
    if not checkstdcontrols(formname, controlname, control):
        passed = False
    if not checknamedcontrol(formname, controlname, control):
        passed = False
    return passed


def formcheck(formname):
    form, controls = load_form_from_json(formname)
    passed = True
    if not checkform(formname, form):
        passed = False

    for control in controls:
        if not checkcontrol(formname, controls[control]["type"], controls[control]):
            passed = False
    return passed


def printmessage(
    ew="ERROR:", form="", table="", field="", data="", message="", moredata=""
):
    print(
        "{ew} {form}:{table}:{field}:{data} - {message} {moredata}".format(
            ew=ew,
            form=form,
            table=table,
            field=field,
            data=data,
            message=message,
            moredata=moredata,
        )
    )


print("\nChecking forms for Errors\n")
DB = clsDB.clsDB("localhost", "ChurchDB", "church", "Church99")
DBConnection = mysql.connector.connect(**DB.DB)
CONFIG.set_Config_DBConnection(DBConnection)

formlist = os.listdir(r".\Forms")
for fn in formlist:
    print("\nChecking", fn)
    formname = os.path.splitext(fn)
    if not formcheck(formname[0]):
        print(formname[0], "Failed")
