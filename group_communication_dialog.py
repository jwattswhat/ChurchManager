"""Reviewed Group recipient preparation and explicit email confirmation UI."""

from __future__ import annotations

from datetime import date

import wx
import wx.adv

from group_communication import GroupCommunicationRepository, GroupCommunicationService
from participant_notifications import configured_mail_service


class GroupCommunicationDialog(wx.Dialog):
    """Show the exact current recipient review before any Group email is sent."""

    def __init__(self, parent, service, group_id):
        super().__init__(parent, title="Group Communication", size=(900, 680),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = service; self.group_id = group_id; self.plan = None
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label=(
            "Review the effective membership and every exclusion. Unlisted contact information is never displayed."
        ))
        note.SetForegroundColour(wx.Colour(0, 82, 155)); outer.Add(note, 0, wx.ALL, 14)
        row = wx.BoxSizer(wx.HORIZONTAL); row.Add(wx.StaticText(panel, label="Effective date"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.effective = wx.adv.DatePickerCtrl(panel); row.Add(self.effective, 0, wx.RIGHT, 10)
        self.review = wx.Button(panel, label="Review Current Recipients"); row.Add(self.review)
        outer.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        self.recipients = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Member", 230), ("Role(s)", 220), ("Email", 280), ("Status", 130))):
            self.recipients.InsertColumn(index, label, width=width)
        outer.Add(self.recipients, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        grid = wx.FlexGridSizer(cols=2, vgap=8, hgap=10); grid.AddGrowableCol(1, 1)
        self.subject = wx.TextCtrl(panel); self.body = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 100))
        for label, control in (("Subject", self.subject), ("Message", self.body)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_TOP); grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); self.send = wx.Button(panel, label="Send Reviewed Message")
        buttons.Add(self.send); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)
        self.review.Bind(wx.EVT_BUTTON, self.on_review); self.send.Bind(wx.EVT_BUTTON, self.on_send)
        self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.send.Disable(); self.on_review()

    def _date(self):
        value = self.effective.GetValue()
        return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())

    def on_review(self, _event=None):
        try: self.plan = self.service.prepare(self.group_id, self._date())
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Review Group Recipients", wx.OK | wx.ICON_ERROR, self); return
        self.subject.SetValue(self.plan.subject); self.body.SetValue(self.plan.body); self.recipients.DeleteAllItems()
        for item in self.plan.recipients:
            row = self.recipients.InsertItem(self.recipients.GetItemCount(), item.name)
            self.recipients.SetItem(row, 1, ", ".join(item.roles) or "Member")
            self.recipients.SetItem(row, 2, item.email if item.status != "Unlisted email" else "")
            self.recipients.SetItem(row, 3, item.status)
            if item.status != "Ready": self.recipients.SetItemTextColour(row, wx.Colour(190, 0, 0))
        self.send.Enable(bool(self.plan.sendable))

    def on_send(self, _event):
        count = len(self.plan.sendable) if self.plan else 0
        if wx.MessageBox(
            f"Send this message to {count} reviewed recipient(s) in '{self.plan.group_name}'?",
            "Confirm Group Communication", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        ) != wx.YES: return
        try: results = self.service.send(self.plan, self.subject.GetValue(), self.body.GetValue())
        except Exception as error:
            wx.MessageBox(str(error), "Group Communication Failed", wx.OK | wx.ICON_ERROR, self); return
        succeeded = sum(bool(item.succeeded) for item in results); failed = len(results) - succeeded
        wx.MessageBox(f"{succeeded} message(s) sent. {failed} failed.", "Group Communication Complete",
                      wx.OK | (wx.ICON_INFORMATION if not failed else wx.ICON_WARNING), self)


def show_group_communication(parent, connection, session, authorization, group_id, test_mode=False):
    """Open a fail-closed, reviewed Group communication dialog."""
    try: mail = configured_mail_service(test_mode=test_mode, connection=connection)
    except Exception: mail = None
    service = GroupCommunicationService(
        GroupCommunicationRepository(connection), session, authorization, mail,
    )
    dialog = GroupCommunicationDialog(parent, service, group_id)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
