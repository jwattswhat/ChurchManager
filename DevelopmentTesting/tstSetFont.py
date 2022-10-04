import wx
from wx.lib import stattext

#---------------------------------------------------------------------------

class TestPanel(wx.Panel):

    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        
        btn = wx.Button(self, -1, "Select Font")
        self.Bind(wx.EVT_BUTTON, self.OnSelectFont, btn)

        self.sampleText = stattext.GenStaticText(self, -1, "Sample Text")
        self.sampleText.SetBackgroundColour(wx.WHITE)

        self.curFont = self.sampleText.GetFont()
        self.curClr = wx.BLACK

        fgs = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        fgs.AddGrowableCol(1)
        fgs.AddGrowableRow(0)

        fgs.Add(btn)
        fgs.Add(self.sampleText, 0, wx.ADJUST_MINSIZE|wx.GROW)

        fgs.Add((15,15)); fgs.Add((15,15))   # an empty row

        fgs.Add(wx.StaticText(self, -1, "PointSize:"))
        self.ps = wx.StaticText(self, -1, "")
        font = self.ps.GetFont()
        font.SetWeight(wx.BOLD)
        self.ps.SetFont(font)
        fgs.Add(self.ps, 0, wx.ADJUST_MINSIZE)

        fgs.Add(wx.StaticText(self, -1, "Family:"))
        self.family = wx.StaticText(self, -1, "")
        self.family.SetFont(font)
        fgs.Add(self.family, 0, wx.ADJUST_MINSIZE)

        fgs.Add(wx.StaticText(self, -1, "Style:"))
        self.style = wx.StaticText(self, -1, "")
        self.style.SetFont(font)
        fgs.Add(self.style, 0, wx.ADJUST_MINSIZE)

        fgs.Add(wx.StaticText(self, -1, "Weight:"))
        self.weight = wx.StaticText(self, -1, "")
        self.weight.SetFont(font)
        fgs.Add(self.weight, 0, wx.ADJUST_MINSIZE)

        fgs.Add(wx.StaticText(self, -1, "Face:"))
        self.face = wx.StaticText(self, -1, "")
        self.face.SetFont(font)
        fgs.Add(self.face, 0, wx.ADJUST_MINSIZE)

        fgs.Add((15,15)); fgs.Add((15,15))   # an empty row

        fgs.Add(wx.StaticText(self, -1, "wx.NativeFontInfo:"))
        self.nfi = wx.StaticText(self, -1, "")
        self.nfi.SetFont(font)
        fgs.Add(self.nfi, 0, wx.ADJUST_MINSIZE)

        # give it some border space
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(fgs, 0, wx.GROW|wx.ADJUST_MINSIZE|wx.ALL, 25)

        self.SetSizer(sizer)
        self.UpdateUI()

    #----------------------------------------------------------------------
    def UpdateUI(self):
        self.sampleText.SetFont(self.curFont)
        self.sampleText.SetForegroundColour(self.curClr)
        self.ps.SetLabel(str(self.curFont.GetPointSize()))
        self.family.SetLabel(str(self.curFont.GetFamily()))
        self.style.SetLabel(str(self.curFont.GetStyle()))
        self.weight.SetLabel(str(self.curFont.GetWeight()))
        self.face.SetLabel(self.curFont.GetFaceName())
        self.nfi.SetLabel(self.curFont.GetNativeFontInfo().ToString())
        self.Layout()

    #----------------------------------------------------------------------
    def OnSelectFont(self, evt):
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(self.curClr)         # set colour
        data.SetInitialFont(self.curFont)

        dlg = wx.FontDialog(self, data)
        
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            colour = data.GetColour()

            self.curFont = font
            self.curClr = colour
            self.UpdateUI()

        # Don't destroy the dialog until you get everything you need from the
        # dialog!
        dlg.Destroy()


########################################################################
class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "wx.FontDialog Tutorial")
        panel = TestPanel(self)
        
#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()