import wx
import wx.richtext as rt


class MainFrame(wx.Frame):
    """Create MainFrame class."""
    def __init__(self):
        """Initialise the class."""
        wx.Frame.__init__(self, None, -1, 'Demonstrate wxPython Rich Text')
        self.panel = MainPanel(self)
        self.refresh_rtf(self.raw_xml())
        self.Centre()

    def refresh_rtf(self, xml):
        handler = wx.richtext.RichTextXMLHandler()
        rtf_buffer = self.rtf_control.GetBuffer()
        rtf_buffer.AddHandler(handler)

        #handler.ImportXML(rtf_buffer, self.rtf_control)
        #self.rtf_control.Refresh()

    def raw_xml(self):
        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<richtext version="1.0.0.0" xmlns="http://www.wxwidgets.org">'
            '<paragraphlayout textcolor="#4C4C4C" fontsize="11"'
                            'fontstyle="90"'
                            'fontweight="90" fontunderlined="0"'
                            'fontface="Ubuntu" alignment="1"'
                            'parspacingafter="10" parspacingbefore="0"'
                            'linespacing="10">'
                '<paragraph>'
                    '<text>"What do we want: "</text>'
                    '<text textcolor="#FF0000">all</text>'
                '</paragraph>'
            '</paragraphlayout>'
        '</richtext>')
        return xml


class MainPanel(wx.Panel):
    """Create a panel class to contain screen widgets."""
    def __init__(self, frame):
        """Initialise the class."""
        wx.Panel.__init__(self, frame)
        rtf_sizer = self._create_rtf_control(frame)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(rtf_sizer, flag=wx.ALL, border=10)
        self.SetSizerAndFit(main_sizer)

    def _create_rtf_control(self, frame):
        rtf_style = wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY|wx.BORDER_SIMPLE
        frame.rtf_control = wx.richtext.RichTextCtrl(self,
                                                 size=(400, 200),
                                                 style=rtf_style)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(frame.rtf_control)
        return sizer


if __name__ == '__main__':
    """Run the application."""
    screen_app = wx.App()
    main_frame = MainFrame()
    main_frame.Show(True)
    screen_app.MainLoop()