import wx
import wx.html2
import threading
import time

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

class Counter():
    def __init__(self,increment):
        self.next_t = time.time()
        self.i=0
        self.done=False
        self.increment = increment
        self.p = wx.Panel(f,size=[500,500])
        self.wv = wx.html2.WebView.New(self.p)
        self._run()

    def _run(self):
        print("hello ", self.i)
        self.next_t+=self.increment
        self.i+=1
        if self.p:
            self.p.Destroy()
        self.p = wx.Panel(f,size=[500,500])
        self.wv = wx.html2.WebView.New(self.p)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.wv, 1, wx.EXPAND, 10) 
        self.p.SetSizer(sizer) 
        self.p.SetSize((700, 700)) 
        self.wv.SetPage(html_string,"")
        f.Show()
        if not self.done:
            threading.Timer( self.next_t - time.time(), self._run).start()
    
    def stop(self):
        self.done=True


app = wx.App()
f = wx.Frame(None,size=[500,500])
p = wx.Panel(f,size=[500,500])
wv = wx.html2.WebView.New(p)
sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(wv, 1, wx.EXPAND, 10) 
p.SetSizer(sizer) 
p.SetSize((700, 700)) 
wv.SetPage(html_string[0],"")
f.Show()
time.sleep(10)
f.Hide()
wv.SetPage(html_string[1],"")
f.Show()
app.MainLoop()

