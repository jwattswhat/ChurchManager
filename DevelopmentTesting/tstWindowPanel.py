from cProfile import label
from distutils.command.build_py import build_py_2to3
import wx

app = wx.App()

frm1 = wx.Frame(None,id=wx.ID_ANY,title="AppTitle",pos=(0,0),size=(500,500))
pan11 = wx.Panel(frm1,id=wx.ID_ANY,size=(500,500),style=wx.TAB_TRAVERSAL)
but11 = wx.Button(pan11,id=wx.ID_ANY,pos=(10,10),label="First")
but12 = wx.Button(pan11,id=wx.ID_ANY,pos=(100,10),label="SeconD")
fld11 = wx.TextCtrl(pan11,id=wx.ID_ANY,pos=(10,50))
fld12 = wx.TextCtrl(pan11,id=wx.ID_ANY,pos=(10,100))

frm2 = wx.Frame(None,id=wx.ID_ANY,title="AppTitle",pos=(100,100),size=(500,500))
pan21 = wx.Panel(frm2,id=wx.ID_ANY,size=(500,500),style=wx.TAB_TRAVERSAL)
but21 = wx.Button(pan21,id=wx.ID_ANY,pos=(10,10),label="First")
but22 = wx.Button(pan21,id=wx.ID_ANY,pos=(100,10),label="SeconD")
fld21 = wx.TextCtrl(pan21,id=wx.ID_ANY,pos=(10,50))
fld22 = wx.TextCtrl(pan21,id=wx.ID_ANY,pos=(10,100))

frm1.Show()
frm2.Show()

app.MainLoop()