"""
    clsFont -  font class
    Rev. Jonathan C. Watt
    July 2022

"""

import pprint
import wx

from clsMonitor import PMON
from clsConfig import CONFIG

DBconnection = None


class clsFont:
    def __init__(self, DBConnection=None):
        self.fontdict = {}
        self._currentfont = wx.Font()
        self.DBConnection = DBConnection

    def set_Font_DBConnection(self, DBConnection):
        self.DBConnection = DBConnection

    def Get_Config_Font(self):
        global CONFIG

        self.fontdict = {}
        strfont = CONFIG.get_Config_Family("Font")
        for f in strfont:
            match f[0]:
                case "PointSize":
                    self.fontdict.update({"pointSize": int(f[1])})
                case "Family":
                    self.fontdict.update({"family": int(f[1])})
                case "Style":
                    self.fontdict.update({"style": int(f[1])})
                case "Weight":
                    self.fontdict.update({"weight": int(f[1])})
                case "Face":
                    self.fontdict.update({"faceName": f[1]})
                case "Underline":
                    self.fontdict.update({"underlined": int(f[1] == 1)})

        self._currentfont = wx.Font(**self.fontdict)
        return self._currentfont

    def chtopt(self, ch):
        global PMON
        return int(PMON.getfontpixelsx(self.fontdict["pointSize"]) * ch)

    def lntopt(self, ln):
        global PMON
        return int(PMON.getfontpixelsy(self.fontdict["pointSize"]) * ln)

    def Get_Current_Font(self):
        return self._currentfont

    def Set_Config_Font(self):
        global CONFIG

        pointsize = self._currentfont.GetPointSize()
        CONFIG.set_Config_Value("FontPointSize", pointsize)
        family = self._currentfont.GetFamily()
        CONFIG.set_Config_Value("FontFamily", family)
        style = self._currentfont.GetStyle()
        CONFIG.set_Config_Value("FontStyle", style)
        weight = self._currentfont.GetWeight()
        CONFIG.set_Config_Value("FontWeight", weight)
        facename = self._currentfont.GetFaceName()
        CONFIG.set_Config_Value("FontFace", facename)
        underlined = self._currentfont.GetUnderlined()
        CONFIG.set_Config_Value("FontUnderlined", underlined == True)

    def Font_Dialog(self, parent):
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(wx.BLACK)
        data.SetInitialFont(self._currentfont)

        dlg = wx.FontDialog(parent, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self._currentfont = font
            dlg.SetFont(font)
            dlg.SetForegroundColour(data.GetColour())
            dlg.Layout()

        dlg.Destroy()

        return self._currentfont


FONT = clsFont()
