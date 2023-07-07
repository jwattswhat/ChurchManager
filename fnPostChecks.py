import os
import wx
import mysql
import subprocess
import json
import argparse
import datetime

import JSForm

import fnFinancial

import fnCMargParse


def _btnPost(event):
    field = event.GetEventObject().GetName()

    #
    #   Check if no Check records
    #

    rec = frm.RECORDS.current()
    lid = fnFinancial.fnposttogl(
        ChurchDB.DBConnection,
        {
            "LedgerID": rec["LedgerID"],
            "ChurchID": rec["ChurchID"],
            "DebitAccountID": rec["DebitAccountID"],
            "CreditAccountID": rec["CreditAccountID"],
            "Description": "Check #" + rec["CheckNumber"],
            "Amount": rec["Amount"],
            "Note": rec["Note"],
        },
    )
    if lid:
        frm.RECORDS.setfieldvalue("LedgerID", lid)
        frm.RECORDS.update_current_record_in_DB()


def _btnPostAll(event):
    field = event.GetEventObject().GetName()

    #
    #   Check if no Check records
    #

    frm.RECORDS.first()
    for r in range(len(frm.RECORDS._record)):
        cr = frm.RECORDS.current()
        lid = fnFinancial.fnposttogl(
            ChurchDB.DBConnection,
            {
                "LedgerID": cr["LedgerID"],
                "ChurchID": cr["ChurchID"],
                "DebitAccountID": cr["DebitAccountID"],
                "CreditAccountID": cr["CreditAccountID"],
                "Description": "Check #" + cr["CheckNumber"],
                "Amount": cr["Amount"],
                "Note": cr["Note"],
            },
        )
        if lid:
            frm.RECORDS.setfieldvalue("LedgerID", lid)
            frm.RECORDS.update_current_record_in_DB()
        frm.RECORDS.next()


app = wx.App(0)

#   Get arguments
host, database, user, password = fnCMargParse.CMargs(
    prog="ChurchManager", description="ChurchManager v.01"
)

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
