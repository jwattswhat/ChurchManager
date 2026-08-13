"""
    fnCMargParse.py - Get the Default Arguments for ChruchManager
    Rev. Jonathan C. Watt
    Copyright: 2023, Jonathan C. Watt
    July 2023

Returns:
    host : mysql db host
    database : database name
    user : user name
    password : user password
"""
import argparse

def CMargs(prog,description,arguments, argv=None):

    cmparser = argparse.ArgumentParser(
        prog=prog, description=description
    )
    if "server" in arguments:
        cmparser.add_argument("-s", "--server", type=str, default="localhost")
    if "database" in arguments:
        cmparser.add_argument("-d", "--database", type=str, default="ChurchDB")
    if "user" in arguments:
        cmparser.add_argument("-u", "--user", type=str)
    if "password" in arguments:
        cmparser.add_argument("-p", "--password", type=str)
    if "reportdate" in arguments:
        cmparser.add_argument("-r","--reportdate",type=str)
    if "churchid" in arguments:
        cmparser.add_argument("--church-id",type=int)
    if "test_mode" in arguments:
        cmparser.add_argument(
            "--test",
            dest="test_mode",
            action="store_true",
            help="Use the configured test database",
        )
    if "jsform_database" in arguments:
        cmparser.add_argument("--jsform-database", type=str, default=None)


    args = cmparser.parse_args(argv)
    # print(args.server,args.database,args.user,args.password)

    returnarguments = {}
    if "server" in arguments:
        returnarguments["server"] = args.server
    if "database" in arguments:
        returnarguments["database"] = args.database
    if "user" in arguments:
        returnarguments["user"] = args.user
    if "password" in arguments:
        returnarguments["password"] = args.password
    if "reportdate" in arguments:
        returnarguments["reportdate"] = args.reportdate
    if "churchid" in arguments:
        returnarguments["churchid"] = args.church_id
    if "test_mode" in arguments:
        returnarguments["test_mode"] = args.test_mode
    if "jsform_database" in arguments:
        returnarguments["jsform_database"] = args.jsform_database

    return returnarguments
