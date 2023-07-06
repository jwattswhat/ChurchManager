import os
import wx
import mysql
import subprocess
import json
import argparse
import datetime

import JSForm

import fnCMargParse

def _btnPost(event):
    field = event.GetEventObject().GetName()
    print (field)
    print (frm.RECORDS.current())

    postdate = datetime.datetime.now().strftime('%m/%d/%Y')

    tblgl = {
        "name":"tblLedger",
        "fields":["*"]
    }
    SQL = JSForm.clsSQL(ChurchDB.DBConnection,tblgl)
    ledgerrec = {
        "ChurchID":frm.RECORDS.current()["ChurchID"],
        "Date": postdate,
        "FiscalYear": JSForm.CONFIG.get_Config_Value("Financial","FiscalYear"),
        "DebitAccountID":frm.RECORDS.current()["DebitAccountID"],
        "CreditAccountID":frm.RECORDS.current()["CreditAccountID"],
        "Description": "Check #"+frm.RECORDS.current()["CheckNumber"],
        "Amount":frm.RECORDS.current()["Amount"],
        "Note":frm.RECORDS.current()["Note"]
    }
    sql = SQL.insert(ledgerrec)
    cursor = ChurchDB.DBConnection.cursor()
    try:
        cursor.execute(sql)
    except Exception as ex:
        print("sql error {err}:{sql} ".format(err=ex,sql=sql))
    ChurchDB.DBConnection.commit()

    # Get the ID (autoincrement field) from the last Insert
    sql = "SELECT Last_Insert_ID();"
    try:
        cursor.execute(sql)
    except Exception as ex:
        print("sql error {err}:{sql} ".format(err=ex,sql=sql))
    lid = cursor.fetchone()
    cursor.close()
    frm.RECORDS.setfieldvalue("LedgerID", lid[0])
    frm.RECORDS.update_current_record_in_DB()
    pass

def _btnPostAll(event):
    field = event.GetEventObject().GetName()
    print (field)
    pass

app = wx.App(0)

#   Get arguments
host,database,user,password = fnCMargParse.CMargs(prog="ChurchManager",description="ChurchManager v.01")

ChurchDB = JSForm.clsDB(host, database, user, password)
JSForm.CONFIG.set_Config_DBConnection(ChurchDB)
JSForm.OPTION.set_Option_DBConnection(ChurchDB)
JSForm.FONT.set_Font_DBConnection(ChurchDB)
JSForm.FONT.Get_Config_Font()
JSForm.CONST.btnNavigationCONTROLS = JSForm.convertNavButtons(
    JSForm.CONST.btnNavigationCONTROLS
)

frm = JSForm.clsForm(None, ChurchDB.DBConnection, "frmPostCheck")

#   Bind keys
frm.CONTROLID["btnPost"].Bind(wx.EVT_BUTTON, _btnPost)
frm.CONTROLID["btnPostAll"].Bind(wx.EVT_BUTTON, _btnPostAll)

frm.show()
app.MainLoop()
