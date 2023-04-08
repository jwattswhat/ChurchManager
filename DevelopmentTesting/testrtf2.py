# wxPython 4 (Phoenix) / Python 3 Version
import wx
import wx.richtext
from io import BytesIO
class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Richtext Test')
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.rt = wx.richtext.RichTextCtrl(self)
        self.rt.SetMinSize((300,200))
        save_button = wx.Button(self, label="Save")
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rt, 1, wx.EXPAND|wx.ALL, 6)
        sizer.Add(save_button, 0, wx.EXPAND|wx.ALL, 6)
        self.SetSizer(sizer)
        self.rt.SetValue(xml)
        self.Show()
    def on_save(self, event):
        out = BytesIO()
        handler = wx.richtext.RichTextXMLHandler()
        rt_buffer = self.rt.GetBuffer()
        handler.SaveFile(rt_buffer, out)
        self.xml_content = out.getvalue()
        print(self.xml_content)

xml = """
<?xml version="1.0" encoding="UTF-8"?>\n<richtext version="1.0.0.0" xmlns="http://www.wxwidgets.org">\n  <paragraphlayout textcolor="#000000" fontpointsize="9" fontfamily="70" fontstyle="90" fontweight="400" fontunderlined="0" fontface="Segoe UI" alignment="1" parspacingafter="10" parspacingbefore="0" linespacing="10" margin-left="5,4098" margin-right="5,4098" margin-top="5,4098" margin-bottom="5,4098">\n    <paragraph>\n      <text>sdfgsdgf alskdjldsafj alfjl;askjfdlasjdf</text>\n    </paragraph>\n    <paragraph>\n      <text>lkasjdljasdflkj</text>\n    </paragraph>\n    <paragraph>\n      <text>alksjdlkajsdf</text>\n    </paragraph>\n    <paragraph>\n      <text></text>\n    </paragraph>\n  </paragraphlayout>\n</richtext>\n
"""

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()