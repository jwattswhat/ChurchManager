import wx



app = wx.App(0)

frm = wx.Frame(None, wx.ID_ANY)
check = wx.CheckBox(frm,wx.ID_ANY,"Testing")
frm.Show()
app.MainLoop()
