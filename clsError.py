import wx
from clsConstants import CONST


class clsErrorNameSpace:
    #    __slots__ = ()

    ERRMSG = "Application Error: \n#{number}\n{msg}"
    ERR = {
        "errno": 0, "msg": "This is an error",  # 0 - Error
        "errno": 1, "msg" : "This is also an error",  # 1 - Another Error

    #   SQL Errors
        "errno" : 1048, "msg": ERRMSG

    }
    ERR0 = 0
    ERRANOTHER = 1


er = clsErrorNameSpace()


class _error:
    def __init__(
        self,
        errno,msg,
        *args
    ):
        print (errno,msg)
        errormessage = er.ERRMSG.format(number=errno, msg=msg)

        panel = wx.Dialog(
            None, id=wx.ID_ANY, title="Application Error", size=[400, 400], pos=[50, 50]
        )
        self.text = wx.StaticText(
            panel,
            wx.ID_ANY,
            label=errormessage,
            pos=(10, 50),
            size=(350,200)
        )
        self.btn = wx.Button(
            panel,
            CONST.FORM_CONTINUE,
            label="Continue",
            size=(100, 30),
            pos=(10, 300),
        )
        self.btn = wx.Button(
            panel, CONST.FORM_CANCEL, label="Cancel", size=(100, 30), pos=(120, 300)
        )

        result = panel.ShowModal()
        panel.Destroy()


class clsErrorHandler(Exception):
    def __init__(self, errno, msg, *args):
        errormessage = _error(errno,msg)
