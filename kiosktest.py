import wx 
import wx.html2 

class MyBrowser(wx.Frame): 
  def __init__(self, *args, **kwds): 
    wx.Dialog.__init__(self, *args, **kwds) 
    sizer = wx.BoxSizer(wx.VERTICAL) 
    self.browser = wx.html2.WebView.New(self) 
    sizer.Add(self.browser, 1, wx.EXPAND, 10) 
    self.SetSizer(sizer) 
    self.SetSize((700, 700)) 

test = "<body><h1><img align=\"left\" \
    src=\'C:\\Users\\jonat\\Documents\\PythonProjects\\ChurchManager\\Pictures\\2012.Luther\'s Seal.MNJW.100dpi.coor.jpg\'\ width=\"200\" height=\"200\">Swaddling Clothes</h1><p>Consider a gift to Swaddling Clothes \
    an outreach of Faith Lutheran Church, Silver Bay. It is a place for moms and moms-to-be to \
    find help gathering items that are needed or a new baby. The 'store' is opening <b>February 18</b>.</p></body>"

if __name__ == '__main__': 
  app = wx.App() 
  dialog = MyBrowser(None, -1) 
  dialog.browser.SetPage(test,"")
  dialog.Show()
  dialog.Maximize(True)
  app.MainLoop() 