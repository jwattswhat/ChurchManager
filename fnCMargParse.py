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

def CMargs(prog,description):

    cmparser = argparse.ArgumentParser(
        prog=prog, description=description
    )
    cmparser.add_argument("-s", "--server", type=str, default="localhost")
    cmparser.add_argument("-d", "--database", type=str, default="ChurchDB")
    cmparser.add_argument("-u", "--user", type=str)
    cmparser.add_argument("-p", "--password", type=str)

    args = cmparser.parse_args()
    # print(args.server,args.database,args.user,args.password)


    host = args.server
    database = args.database
    user = args.user
    password = args.password

    return host,database,user,password