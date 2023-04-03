import os, sys
import wx
import wx.lib.plot as plot
import image

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500, 500))

        HolderPanel = wx.Panel(self, wx.ID_ANY)

        panel2 = MyPanel_2(HolderPanel, wx.ID_ANY)

        framesizer = wx.BoxSizer(wx.HORIZONTAL)
        framesizer.Add(panel2, 1, wx.EXPAND | wx.BOTTOM | wx.TOP | wx.RIGHT, 2)

        HolderSizer = wx.BoxSizer(wx.VERTICAL)
        HolderSizer.Add(framesizer, 1, wx.EXPAND)

        HolderPanel.SetSizer(HolderSizer)
        self.Show()


class MyPanel_2(wx.Panel):

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour('grey')


        # Create main image holder
        self.img_1 = wx.EmptyImage(300,300)        
        self.imageCtrl_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.img_1)) # Starting with an EmptyBitmap, the real one will get put there by the call onView
        self.PhotoMaxSize_1 = (300)
        self.imageCtrl_1.Bind(wx.EVT_LEFT_DOWN, self.onMouseClick_img1)

        # Create the browse button
        brwsBtn = wx.Button(self, wx.ID_ANY, 'Browse', (10, 10))
        brwsBtn.Bind(wx.EVT_BUTTON, self.onBrowse)

        # Set up the text box
        self.photoTxt = wx.TextCtrl(self, size=(200,-1))

        # Create the sizers
        vsizer1 = wx.BoxSizer(wx.VERTICAL)
        hsizer3 = wx.BoxSizer(wx.HORIZONTAL)
        vsizer_MAIN = wx.BoxSizer(wx.VERTICAL)

        # -----------------------------------------------------------------------------------------------------------
        vsizer1.Add(self.imageCtrl_1, proportion = 0, flag= wx.ALIGN_CENTRE | wx.ALL, border=10)

        # -----------------------------------------------------------------------------------------------------------
        hsizer3.Add(brwsBtn, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.RIGHT, border=10)
        hsizer3.Add(self.photoTxt, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.RIGHT, border = 10)

        # -----------------------------------------------------------------------------------------------------------
        vsizer_MAIN.Add(vsizer1, proportion = 1, flag = wx.EXPAND)
        vsizer_MAIN.Add(hsizer3, proportion = 1, flag = wx.EXPAND)

        # -----------------------------------------------------------------------------------------------------------
        self.SetSizer(vsizer_MAIN)

    def onBrowse(self, event):
        """ 
        Browse for file
        """
        wildcard = "pictures (*.jpg, *.jpeg, *.png)|*.jpg;*.jpeg;*.png"
        dialog = wx.FileDialog(None, "Choose a file", wildcard=wildcard, style=wx.OPEN)

        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy() 
        self.onView()

    def onView(self):

        self.filepath = self.photoTxt.GetValue()

        self.img_1 = wx.Image(self.filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = self.img_1.GetWidth()
        H = self.img_1.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize_1
            NewH = self.PhotoMaxSize_1 * H / W
        else:
            NewH = self.PhotoMaxSize_1
            NewW = self.PhotoMaxSize_1 * W / H
        self.img_1 = self.img_1.Scale(NewW,NewH)

        self.imageCtrl_1.SetBitmap(wx.BitmapFromImage(self.img_1)) # Converts the scaled image to a wx.Bitmap and put it on the wx.StaticBitmap
        self.Refresh()

    def onMouseClick_img1(self, event):

        im = Image.open(self.filepath)
        pos = event.GetPosition()
        pix = im.load()
        print (pix[pos.x, pos.y])

app = wx.App()
MyFrame(None, -1, 'Current Build')
app.MainLoop()