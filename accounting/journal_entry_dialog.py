"""Printable journal-entry view and standalone HTML export."""
from datetime import datetime
from html import escape
from pathlib import Path
import os

import wx

from .formatting import money


def _text(value):
    return "" if value is None else str(value)


def journal_entry_html(report):
    h = report["header"]
    rows = []
    total_debit = total_credit = 0
    for line in report["lines"]:
        total_debit += line[6]; total_credit += line[7]
        cells = [line[0], *line[1:6], money(line[6]), money(line[7])]
        rows.append("<tr>" + "".join("<td{}>{}</td>".format(' class="amount"' if index >= 6 else "", escape(_text(value))) for index, value in enumerate(cells)) + "</tr>")
    attachments = "".join("<li>{} ({}) - SHA-256 {}</li>".format(escape(_text(item[0])), escape(_text(item[1])), escape(_text(item[2]))) for item in report["attachments"])
    if not attachments:
        attachments = "<li>None</li>"
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    return """<!doctype html><html><head><meta charset=\"utf-8\"><title>Journal Entry {number}</title>
<style>body{{font-family:Arial,sans-serif;margin:32px;color:#111}}h1{{margin-bottom:4px}}.meta{{display:grid;grid-template-columns:180px 1fr;gap:5px 12px;margin:20px 0}}table{{border-collapse:collapse;width:100%;font-size:12px}}th,td{{border:1px solid #999;padding:5px;text-align:left}}th{{background:#eee}}.amount{{text-align:right;white-space:nowrap}}.total{{font-weight:bold}}@media print{{button{{display:none}}body{{margin:12mm}}}}</style></head><body>
<button onclick=\"window.print()\">Print</button><h1>Journal Entry #{number}</h1><div>{organization}</div>
<div class=\"meta\"><b>Date</b><span>{date}</span><b>Type / status</b><span>{kind} / {status}</span><b>Description</b><span>{description}</span><b>Reference</b><span>{reference}</span><b>Created</b><span>{created_at} by {creator}</span><b>Reviewed</b><span>{reviewed_at} by {reviewer}</span><b>Posted</b><span>{posted_at} by {poster}</span><b>Original / reversal</b><span>{original} / {reversal}</span></div>
<table><thead><tr><th>#</th><th>Account</th><th>Fund</th><th>Function</th><th>Payee</th><th>Description</th><th class=\"amount\">Debit</th><th class=\"amount\">Credit</th></tr></thead><tbody>{rows}<tr class=\"total\"><td colspan=\"6\">Totals</td><td class=\"amount\">{debits}</td><td class=\"amount\">{credits}</td></tr></tbody></table>
<h2>Attachments</h2><ul>{attachments}</ul><p>Generated {generated}</p></body></html>""".format(
        number=escape(_text(h[1])), organization=escape(_text(h[2])), date=escape(_text(h[3])), kind=escape(_text(h[4])), status=escape(_text(h[5])), description=escape(_text(h[6])), reference=escape(_text(h[7])), created_at=escape(_text(h[8])), creator=escape(_text(h[9])), reviewed_at=escape(_text(h[10])), reviewer=escape(_text(h[11])), posted_at=escape(_text(h[12])), poster=escape(_text(h[13])), original=escape(_text(h[14])), reversal=escape(_text(h[15])), rows="".join(rows), debits=money(total_debit), credits=money(total_credit), attachments=attachments, generated=escape(generated))


class JournalEntryDialog(wx.Dialog):
    def __init__(self, parent, report, report_service=None):
        super().__init__(parent, title="Journal Entry Report", size=(1050, 700))
        self.report = report; self.report_service=report_service; h = report["header"]
        details = wx.StaticText(self, label="Transaction #{}    {}    {}    {}\n{}\nReference: {}\nCreated by {}    Reviewed by {}    Posted by {}\nOriginal: {}    Reversal: {}".format(h[1], h[2], h[3], h[5], h[6], h[7], h[9], h[11] or "(none)", h[13] or "(none)", h[14] or "(none)", h[15] or "(none)"))
        self.lines = wx.ListCtrl(self, style=wx.LC_REPORT)
        for i,(label,width) in enumerate((("#",35),("Account",190),("Fund",135),("Function",110),("Payee",100),("Description",180),("Debit",90),("Credit",90))):
            self.lines.InsertColumn(i,label,format=wx.LIST_FORMAT_RIGHT if i>=6 else wx.LIST_FORMAT_LEFT,width=width)
        for item in report["lines"]:
            row=self.lines.InsertItem(self.lines.GetItemCount(),str(item[0]))
            for column,value in enumerate((*item[1:6],money(item[6]),money(item[7])),1): self.lines.SetItem(row,column,str(value))
        names = ", ".join(item[0] for item in report["attachments"]) or "None"
        attachments = wx.StaticText(self,label="Attachments: " + names)
        save = wx.Button(self,label="Save / Print Report (HTML)");pdf=wx.Button(self,label="Preview PDF"); close=wx.Button(self,wx.ID_CLOSE,"Close")
        save.Bind(wx.EVT_BUTTON,self.on_save);pdf.Bind(wx.EVT_BUTTON,self.on_pdf);pdf.Enable(report_service is not None); close.Bind(wx.EVT_BUTTON,lambda event:self.EndModal(wx.ID_CLOSE))
        buttons=wx.BoxSizer(wx.HORIZONTAL);buttons.Add(save);buttons.Add(pdf,0,wx.LEFT,8);buttons.AddStretchSpacer();buttons.Add(close)
        root=wx.BoxSizer(wx.VERTICAL);root.Add(details,0,wx.ALL|wx.EXPAND,10);root.Add(self.lines,1,wx.LEFT|wx.RIGHT|wx.EXPAND,10);root.Add(attachments,0,wx.ALL|wx.EXPAND,10);root.Add(buttons,0,wx.ALL|wx.EXPAND,10);self.SetSizer(root)
    def on_save(self,event):
        number=self.report["header"][1]
        dialog=wx.FileDialog(self,"Save Journal Entry",wildcard="HTML files (*.html)|*.html",defaultFile="JournalEntry-{}.html".format(number),style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        try:
            if dialog.ShowModal()!=wx.ID_OK:return
            path=Path(dialog.GetPath());path.write_text(journal_entry_html(self.report),encoding="utf-8");os.startfile(str(path))
        finally:dialog.Destroy()
    def on_pdf(self,event):
        try:self.report_service.run_journal_entry(self.report["header"][0])
        except Exception as error:wx.MessageBox(str(error),"Journal Entry PDF",wx.OK|wx.ICON_ERROR,self)
