import os
import json
from turtle import position
import mysql

from clsConfig import CONFIG
import clsDB

CHECKPOSITION = {
    "pos": {"vartype": "<class 'list'>", "required": True, "dependency": "size"},
    "posch": {"vartype": "<class 'list'>", "required": True, "dependency": "sizech"},
}

CHECKSIZE = {
    "size": {"vartype": "<class 'list'>", "required": True, "dependency": "pos"},
    "sizech": {"vartype": "<class 'list'>", "required": True, "dependency": "posch"},
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
    **{
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
        #    "table": CHECKTABLE,
    },
    **CHECKPOSITION,
    **CHECKSIZE,
    **{
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
    },
}

CHECKSTDCONTROLS = {
    **{
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
    },
    **CHECKPOSITION,
    **CHECKSIZE,
    **{
        #    "table": {},
        "stylelist": {
            "vartype": "<class 'list'>",
            "required": False,
            "values": [
                "MULTILINE",
                "DONTWRAP",
                "WORDWRAP",
                "PROCESSENTER",
                "PROCESSTAB",
                "READONLY",
            ],
        },
    },
}

CHECKNAMEDCONTROLS = {
    "StaticBox": {
        "label": {"vartype": "<class 'str'>", "required": True},
    },
    "StaticText": {"label": {"vartype": "<class 'str'>", "required": True}},
    "TextCtrl": {
        "value": {"vartype": "<class 'str'>", "required": True},
        "lookupchoices": {
            "required": False,
        },
    },
    "MultiLine": {},
    "ComboBox": {
        "value": {"vartype": "<class 'str'>", "required": True},
        "choices": {
            "vartype": "<class 'list",
            "required": False,
        },
        "refreshform": {"vartype": "<class 'bool'>", "required": False},
    },
    "CheckBox": {
        "value": {"vartype": "<class 'str'>", "required": True},
    },
    "CheckListBox": {
        "label": {"vartype": "<class 'str'>", "required": True},
        "choices": {"vartype": "<class 'list", "required": False},
    },
    "Button": {
        "id": {"vartype": "<class 'int'>", "required": True},
        "label": {"vartype": "<class 'str'>", "required": True},
        "open": {"vartype": "<class 'str'", "required": False},
    },
    "DataViewListCtrl": {
        "position": {},
        "table": CHECKTABLE,
        "columns": {},
    },
    "DateTime": {"id": {}, "size": {}, "sizech": {}, "dt": {}},
    "DatePickerCtrl": {"id": {}, "size": {}, "sizech": {}, "dt": {}},
    "TimePickerCtrl": {},
    "CalendarCtrl": {},
    "FilePickerCtrl": {},
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


def checksql():
    cursor = DBConnection.cursor()
    match checkfield:
        case "name":
            sql = "SELECT * FROM {formname} LIMIT 1;".format(formname=formname)
            try:
                cursor.execute(sql)
                row = cursor.fetchone()
            except Exception as ex:
                passed = False
                printmessage(form=formname, table=tablename, message="table, not found")

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


##################################################


def checkrequired(formname, check, tocheck):
    passed = True
    for checkfield in check:
        if check[checkfield]["required"]:
            if checkfield not in tocheck:
                printmessage(form=formname, field=checkfield, message=" field reqired")
                passed = False
    return passed


def checkdepedency(formname, check, tocheck):
    passed = True
    for checkfield in check:
        if "dependency" in check[checkfield]:
            if check[checkfield]["dependency"] not in tocheck:
                printmessage(
                    form=formname,
                    field=checkfield,
                    message=" dependency missing for field",
                    moredata=check[checkfield]["dependency"],
                )
                passed = False
    return passed


def check(formname, tablename, check, tocheck):
    passed = True

    #   check for required fields
    if not checkrequired(formname, check, tocheck):
        passed = False

    #   check for field dependencies
    if not checkdepedency(formname, check, tocheck):
        passed = False

    for tocheckfield in tocheck:
        print("\tchecking", tocheckfield)
        tocheckdata = tocheck.get(tocheckfield, None)

        #   check for extra data, ignored
        if tocheckfield not in check:
            printmessage(
                "WARNING:",
                form=formname,
                table=tablename,
                field=tocheckfield,
                data=tocheckdata,
                message="field not found, ignored",
            )
            continue

        #   check if correct type
        if str(type(tocheckdata)) != check[tocheckfield]["vartype"]:
            printmessage(
                form=formname,
                table=tablename,
                field=tocheckfield,
                data=tocheckdata,
                message=" invalid data type expecting "
                + check[tocheckfield]["vartype"]
                + " found ",
                moredata=str(type(tocheckdata)),
            )
            passed = False

    return passed


def checkposition(formname, check, tocheck):
    passed = True
    passed = checkdepedency(formname, check, tocheck)

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


def checkwholeform(formname):
    tocheckform, tocheckcontrols = load_form_from_json(formname)
    passed = True

    #   check form details
    if not check(formname, "", CHECKFORM, tocheckform):
        passed = False

    for control in tocheckcontrols:
        if control not in CHECKSTDCONTROLS:
            print("\tchecking", control)
            if not check(
                formname,
                tocheckcontrols[control]["type"],
                CHECKSTDCONTROLS,
                tocheckcontrols[control],
            ):
                passed = False
            if tocheckcontrols[control]["type"] not in CHECKNAMEDCONTROLS:
                printmessage(
                    form=formname,
                    field="type",
                    data=tocheckcontrols[control]["type"],
                    message=" invalid control",
                )
                passed = False
            elif not check(
                formname,
                tocheckcontrols[control]["type"],
                CHECKNAMEDCONTROLS[tocheckcontrols[control]["type"]],
                tocheckcontrols[control],
            ):
                passed = False

    return passed


def printmessage(
    ew="ERROR:", form="", table="", field="", data="", message="", moredata=""
):
    print(
        "\t\t{ew} {form}:{table}:{field}:{data} - {message} {moredata}".format(
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
    formname = os.path.splitext(fn)
    print("\nChecking", formname[0])
    if not checkwholeform(formname[0]):
        print(formname[0], "Failed")
