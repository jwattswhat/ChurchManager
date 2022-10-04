# !/usr/bin/env python3
from typing import Text
import wx
from wx.core import TextCtrl
from datetime import datetime
import functions

mfdict = {
    'title': 'datetest',
    'pos': wx.Point(10, 10),
    'size': wx.Size(500,500),
    'name': 'datetest'
}
mfield = {
    'Date': {
        'value': '2021-12-01',
        'pos': wx.Point(10,50),
        'size': wx.Size(300, 30),
        'name': 'Date',
    },
    'Label': {
            'label': 'Enter Date:',
            'pos': wx.Point(10, 10),
            'name': 'Label'
    },
    'Button': {
        'label' : 'OK',
        'pos': wx.Point(400, 400),
        'name': 'Close'
    }
}

class MainForm():
    FORM = 0
    LBL = 0
    FLD = 0
    BTN = 0
    def __init__(self, frm):
        self.FORM = wx.Frame(None, -1, **frm )


    def setfield(self, fld):
        self.LBL = wx.StaticText(self.FORM, -1, **fld['Label'])
        self.FLD = wx.TextCtrl(self.FORM, -1,**fld['Date'] )
        self.BTN = wx.Button( self.FORM, -1, **fld['Button'])
        self.FORM.Bind(wx.EVT_BUTTON, self.onOK, self.BTN)

    def onOK(self, event):
        strdate = self.FLD.GetValue()
        print ("Date is: ",strdate)

        dt = functions.SQLdate_to_date(strdate)
        sdt = functions.date_to_SQLDate(dt)

        print (type(dt),dt)
        print (type(sdt),sdt)
    
        print ('done')

app = wx.App(0)

mfr = MainForm(mfdict)
mfr.setfield(mfield) 
mfr.FORM.Show(True)

app.MainLoop()