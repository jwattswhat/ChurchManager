import wx

class MainWin(wx.Frame):
    def __init__(self):
        super().__init__(None, title='My modal window')
        ####---- Variables
        self.frameFvar = None
        ####---- Widgets
        self.panel = wx.Panel(self)
        self.buttonF = wx.Button(self.panel, label='Show Normal')
        self.buttonM = wx.Button(self.panel, label='Show Modal')
        ####---- Sizer
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.buttonF, border=20, flag=wx.ALIGN_CENTER|wx.ALL)
        self.sizer.Add(self.buttonM, border=20, flag=wx.ALIGN_CENTER|wx.ALL)
        self.sizerM = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerM.Add(self.sizer, border=20, 
            flag=wx.EXPAND ) #|wx.ALIGN_CENTER|wx.ALL)
        self.panel.SetSizer(self.sizerM)
        self.sizerM.Fit(self)
        ####---- Position
        self.SetPosition(pt=(50, 50))
        ####---- Bind
        self.buttonF.Bind(wx.EVT_BUTTON, self.ShowAsNormal)
        self.buttonM.Bind(wx.EVT_BUTTON, self.ShowAsModal)
    #---

    def ShowAsNormal(self, event):
        if self.frameFvar == None:
            self.frameF = AsFrame(self)
            self.frameF.Show()
            self.frameFvar = True
        else:
            self.frameF.Raise()
    #---

    def ShowAsModal(self, event):
        self.frameM = AsDialog(self)
        if self.frameM.ShowModal() == wx.ID_OK:
            print("Exited by Ok button")
        else:
            print("Exited by X button")
        self.frameM.Destroy()
    #---
#---


class AsFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent=parent, title='Shown as a wx.Frame')
        ####---- Variables
        self.parent = parent
        ####---- Widgets
        self.a = MyPanel(self)
        ####---- Position
        self.SetPosition(pt=(50, 200))
        ####---- Bind
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    #---

    def OnClose(self, event):
        self.parent.frameFvar = None
        self.Destroy()
    #---
#---


class AsDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent=parent, title='Shown as a wx.Dialog')
        ####---- Variables
        self.SetEscapeId(12345)
        ####---- Widgets
        self.a = MyPanel(self)
        self.buttonOk = wx.Button(self, wx.ID_OK)
        ####---- Sizers
        self.sizerB = wx.StdDialogButtonSizer()
        self.sizerB.AddButton(self.buttonOk)
        self.sizerB.Realize()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.a, border=10, flag=wx.EXPAND|wx.ALIGN_LEFT|wx.ALL)
        self.sizer.Add(self.sizerB, border=10, 
            flag=wx.EXPAND) #|wx.ALIGN_RIGHT|wx.ALL)

        self.SetSizer(self.sizer)

        ####---- Position
        self.SetPosition(pt=(550, 200))
    #---       
#---


class MyPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        ####---- Variables
        self.parent = parent
        ####---- Widgets
        label = ("The same window shown as a wx.Frame or a wx.Dialog")
        self.text = wx.StaticText(self, label=label, pos=(10, 10))
    #---
#---


if __name__ == '__main__':
    app = wx.App()
    frameM = MainWin()
    frameM.Show()
    app.MainLoop()