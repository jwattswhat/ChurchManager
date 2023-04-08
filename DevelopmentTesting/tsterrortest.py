import wx
import clsError

def err(event):
    raise clsError.clsErrorHandler(1)


app = wx.App(0)

FRAME = wx.Frame(
    None,
    id=wx.ID_ANY,
    title="Error Test",
    pos=[0,0],
    size=[400,400]
)
STR = wx.StaticText(FRAME,pos=[0,0],label="Error Test")
BUTTON = wx.Button(FRAME,pos=[50,50],label="Error",size=[60,30])
BUTTON.Bind(wx.EVT_LEFT_DOWN, err)


FRAME.Show()

app.MainLoop()
