"""Review-first participant notification screen."""

from __future__ import annotations

import wx

from participant_notifications import (
    ParticipantNotificationRepository, ParticipantNotificationService,
    configured_mail_service,
)


class ParticipantNotificationDialog(wx.Dialog):
    def __init__(self, parent, service, processes):
        super().__init__(parent, title="Notify Worship Participants", size=(1050, 720))
        self.service = service
        self.processes = processes
        self.services = service.repository.services()
        self.plan = None

        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        instructions = wx.StaticText(panel, label=(
            "Review every recipient and generate the current Worship Planning report. "
            "Email is sent only after your final confirmation."
        ))
        outer.Add(instructions, 0, wx.ALL, 10)

        service_row = wx.BoxSizer(wx.HORIZONTAL)
        service_row.Add(wx.StaticText(panel, label="Service"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.service_choice = wx.Choice(panel, choices=[row[1] for row in self.services])
        service_row.Add(self.service_choice, 1, wx.EXPAND)
        outer.Add(service_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.recipients = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Participant", 210), ("Position(s)", 230), ("Email", 300), ("Status", 150),
        )):
            self.recipients.InsertColumn(index, label, width=width)
        outer.Add(self.recipients, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        fields = wx.FlexGridSizer(2, 2, 8, 8); fields.AddGrowableCol(1, 1)
        fields.Add(wx.StaticText(panel, label="Subject"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.subject = wx.TextCtrl(panel); fields.Add(self.subject, 1, wx.EXPAND)
        fields.Add(wx.StaticText(panel, label="Message"), 0, wx.ALIGN_TOP)
        self.body = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 105)); fields.Add(self.body, 1, wx.EXPAND)
        outer.Add(fields, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.attachment = wx.StaticText(panel, label="Attachment: Not generated")
        outer.Add(self.attachment, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.generate = wx.Button(panel, label="Generate Current Report")
        self.preview = wx.Button(panel, label="Preview Report")
        self.send = wx.Button(panel, label="Send")
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        for button in (self.generate, self.preview, self.send): buttons.Add(button, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer(); buttons.Add(close)
        outer.Add(buttons, 0, wx.ALL | wx.EXPAND, 10)
        panel.SetSizer(outer)

        self.service_choice.Bind(wx.EVT_CHOICE, self.on_service)
        self.generate.Bind(wx.EVT_BUTTON, self.on_generate)
        self.preview.Bind(wx.EVT_BUTTON, self.on_preview)
        self.send.Bind(wx.EVT_BUTTON, self.on_send)
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        self.preview.Disable(); self.send.Disable()
        if self.services:
            self.service_choice.SetSelection(0); self.on_service()

    def on_service(self, _event=None):
        index = self.service_choice.GetSelection()
        if index == wx.NOT_FOUND: return
        try:
            self.plan = self.service.prepare(self.services[index][0])
        except Exception as error:
            wx.MessageBox(str(error), "Unable to review notification", wx.OK | wx.ICON_ERROR, self); return
        self.subject.SetValue(self.plan.subject); self.body.SetValue(self.plan.body)
        self.attachment.SetLabel("Attachment: Not generated")
        self.preview.Disable(); self.send.Disable(); self._fill_recipients()

    def _fill_recipients(self):
        self.recipients.DeleteAllItems()
        for recipient in self.plan.recipients:
            row = self.recipients.InsertItem(self.recipients.GetItemCount(), recipient.name)
            self.recipients.SetItem(row, 1, ", ".join(recipient.positions))
            self.recipients.SetItem(row, 2, recipient.email)
            self.recipients.SetItem(row, 3, recipient.status)
            if recipient.status != "Ready": self.recipients.SetItemTextColour(row, wx.Colour(190, 0, 0))

    def on_generate(self, _event):
        try:
            self.plan = self.service.generate_attachment(self.plan)
        except Exception as error:
            wx.MessageBox(str(error), "Report Generation Failed", wx.OK | wx.ICON_ERROR, self); return
        self.attachment.SetLabel("Attachment: {}".format(self.plan.attachment.name))
        self.preview.Enable(); self.send.Enable(bool(self.plan.sendable_addresses))

    def on_preview(self, _event):
        if self.plan and self.plan.attachment: self.processes.open_file(self.plan.attachment)

    def on_send(self, _event):
        count = len(self.plan.sendable_addresses)
        confirmation = wx.MessageBox(
            "Send {} message(s) with attachment '{}'?".format(count, self.plan.attachment.name),
            "Confirm Participant Notification", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        )
        if confirmation != wx.YES: return
        try:
            results = self.service.send(self.plan, self.subject.GetValue(), self.body.GetValue())
        except Exception as error:
            wx.MessageBox(str(error), "Notification Failed", wx.OK | wx.ICON_ERROR, self); return
        succeeded = sum(result.succeeded for result in results)
        failed = len(results) - succeeded
        wx.MessageBox(
            "{} message(s) sent. {} failed.".format(succeeded, failed),
            "Notification Complete", wx.OK | (wx.ICON_INFORMATION if not failed else wx.ICON_WARNING), self,
        )


def show_participant_notifications(parent, connection, authorization, reports, processes):
    repository = ParticipantNotificationRepository(connection)
    try:
        mail = configured_mail_service()
    except Exception:
        mail = None
    service = ParticipantNotificationService(repository, authorization, reports, mail)
    dialog = ParticipantNotificationDialog(parent, service, processes)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
