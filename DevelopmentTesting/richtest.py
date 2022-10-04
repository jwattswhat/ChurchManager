import wx
import wx.richtext


app = wx.App(0)
frm = wx.Frame(parent=None,pos=[10,10],size=[500,500])
pnl = wx.Panel(frm)
rt = wx.richtext.RichTextCtrl(pnl,-1,pos=[100,100],size=[100,100])

frm.Show()
app.MainLoop()