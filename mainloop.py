#!/usr/bin/env python

"""
This demo attempts to override the C++ MainLoop and implement it
in Python.
"""

import time
import wx
import wx.lib.newevent as ne
import wx.html2


##import os; raw_input('PID: %d\nPress enter...' % os.getpid())

GooEvent, EVT_GOO = ne.NewCommandEvent()

#---------------------------------------------------------------------------
html_string = ["""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
    <head>
       <title>Hello World!</title>
       <script type="text/javascript" src="jquery.js"></script>
       <style type="text/css" src="main.css"></style>
    </head>
    <body>
        <span id="foo">The quick brown fox jumped over the lazy dog</span>
        <script type="text/javascript">
        $(document.ready(function(){
           $(#"span#foo").click(function(){ alert('I was clicked!'); });
         });
        </script>
    </body>
</html>
""",
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
    <head>
       <title>Hello World!</title>
       <script type="text/javascript" src="jquery.js"></script>
       <style type="text/css" src="main.css"></style>
    </head>
    <body>
        <span id="foo">The <b>very</b> quick brown fox jumped over the lazy dog</span>
        <script type="text/javascript">
        $(document.ready(function(){
           $(#"span#foo").click(function(){ alert('I was clicked!'); });
         });
        </script>
    </body>
</html>
"""]


#---------------------------------------------------------------------------

class MyEventLoop(wx.GUIEventLoop):
    counter = 0
    def __init__(self):
        wx.GUIEventLoop.__init__(self)
        self.exitCode = 0
        self.shouldExit = False

    def DoMyStuff(self):
        global wv
        self.counter+=1
        if self.counter > 1:
            self.counter = 0
        wv.SetPage(html_string[self.counter],"")
        time.sleep(10)

    def Run(self):
        # Set this loop as the active one. It will automatically reset to the
        # original evtloop when the context manager exits.
        with wx.EventLoopActivator(self):
            while True:

                self.DoMyStuff()

                # Generate and process idles events for as long as there
                # isn't anything else to do
                while not self.shouldExit and not self.Pending() and self.ProcessIdle():
                    pass

                if self.shouldExit:
                    break

                # Dispatch all the pending events
                self.ProcessEvents()

                # Currently on wxOSX Pending always returns true, so the
                # ProcessIdle above is not ever called. Call it here instead.
                if 'wxOSX' in wx.PlatformInfo:
                    self.ProcessIdle()

            # Process remaining queued messages, if any
            while True:
                checkAgain = False
                if wx.GetApp() and wx.GetApp().HasPendingEvents():
                    wx.GetApp().ProcessPendingEvents()
                    checkAgain = True
                if 'wxOSX' not in wx.PlatformInfo and self.Pending():
                    self.Dispatch()
                    checkAgain = True
                if not checkAgain:
                    break

        return self.exitCode


    def Exit(self, rc=0):
        self.exitCode = rc
        self.shouldExit = True
        self.OnExit()
        self.WakeUp()


    def ProcessEvents(self):
        if wx.GetApp():
            wx.GetApp().ProcessPendingEvents()

        if self.shouldExit:
            return False

        return self.Dispatch()

class MyApp(wx.App):

    def MainLoop(self):
        self.SetExitOnFrameDelete(True)
        self.mainLoop = MyEventLoop()
        self.mainLoop.Run()

    def ExitMainLoop(self):
        self.mainLoop.Exit()

    def OnInit(self):
        global wv
        frame = wx.Frame(None, -1)
        panel = wx.Panel(frame)
        wv = wx.html2.WebView.New(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wv, 1, wx.EXPAND, 10) 
        panel.SetSizer(sizer) 
        panel.SetSize((700, 700)) 
        wv.SetPage(html_string[0],"")
        frame.Show(True)
        self.SetTopWindow(frame)

        #self.keepGoing = True
        return True

wv = 0
app = MyApp(False)
app.MainLoop()

