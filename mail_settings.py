"""Protected SMTP settings backed by Windows Credential Manager."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import wx
import JSForm

from bulletin_orders import portable_connection
from participant_notifications import TestModeMailService


CREDENTIAL_TARGET = "ChurchManager/SMTP"


@dataclass(frozen=True)
class ChurchMailSettings:
    enabled: bool = False
    server: str = ""
    port: int = 587
    security: str = "STARTTLS"
    username: str = ""
    sender_address: str = ""
    sender_name: str = "ChurchManager"
    reply_to: str = ""
    credential_target: str = CREDENTIAL_TARGET
    timeout: int = 30


class MailSettingsRepository:
    """Persist non-secret mail settings in the active ChurchManager database."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def load(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT Enabled,Server,Port,Security,UserName,SenderAddress,SenderName,"
                "ReplyTo,CredentialTarget,TimeoutSeconds FROM tblMailSettings WHERE ID=1"
            )
            row = cursor.fetchone()
        finally:
            cursor.close()
        return ChurchMailSettings(*row) if row else ChurchMailSettings()

    def save(self, value):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblMailSettings SET Enabled=?,Server=?,Port=?,Security=?,UserName=?,"
                "SenderAddress=?,SenderName=?,ReplyTo=?,CredentialTarget=?,TimeoutSeconds=? WHERE ID=1",
                (value.enabled, value.server, value.port, value.security, value.username,
                 value.sender_address, value.sender_name, value.reply_to,
                 value.credential_target, value.timeout),
            )
            self.connection.commit()
        finally:
            cursor.close()

    def record_test(self, status):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblMailSettings SET LastTestAt=?,LastTestStatus=? WHERE ID=1",
                (datetime.now(), str(status)[:255]),
            )
            self.connection.commit()
        finally:
            cursor.close()


class ChurchMailServiceFactory:
    """Build mail delivery only after settings and protected credentials validate."""

    def __init__(self, connection, test_mode=False, credential_store=None):
        self.repository = MailSettingsRepository(connection)
        self.test_mode = bool(test_mode)
        self.credentials = credential_store or JSForm.WindowsCredentialStore()

    def build(self):
        if self.test_mode:
            return TestModeMailService()
        value = self.repository.load()
        if not value.enabled:
            raise JSForm.MailConfigurationError("Email delivery is not enabled.")
        try:
            stored_username, password = self.credentials.read(value.credential_target)
        except KeyError as error:
            raise JSForm.MailConfigurationError("No protected email password is stored.") from error
        username = value.username or stored_username
        settings = JSForm.MailSettings(
            value.server, value.port, username or None, password or None,
            value.sender_address, value.sender_name, value.security.casefold(),
            value.reply_to or None,
        )
        settings.validate()
        return JSForm.MailService(JSForm.SMTPTransport(settings, timeout=value.timeout))


class MailSettingsDialog(wx.Dialog):
    """Edit non-secret email settings and explicitly manage the protected password."""

    def __init__(self, parent, connection, authorization, test_mode=False):
        authorization.require("application.config.manage", "manage email settings")
        super().__init__(parent, title="Email Settings", size=(650, 570),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = MailSettingsRepository(connection)
        self.factory = ChurchMailServiceFactory(connection, test_mode)
        self.test_mode = bool(test_mode)
        value = self.repository.load()
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label=(
            "Configure outgoing ChurchManager email. The password is stored by Windows, "
            "never in the database or configuration files."
        ))
        note.Wrap(600); outer.Add(note, 0, wx.ALL | wx.EXPAND, 12)
        grid = wx.FlexGridSizer(cols=2, hgap=10, vgap=8); grid.AddGrowableCol(1, 1)
        self.enabled = wx.CheckBox(panel, label="Enable outgoing email")
        self.enabled.SetValue(value.enabled); grid.Add(wx.StaticText(panel, label="Status:"), 0, wx.ALIGN_CENTER_VERTICAL); grid.Add(self.enabled)
        self.server = wx.TextCtrl(panel, value=value.server); self._row(grid, panel, "SMTP server:", self.server)
        self.port = wx.SpinCtrl(panel, min=1, max=65535, initial=value.port); self._row(grid, panel, "Port:", self.port)
        self.security = wx.Choice(panel, choices=["STARTTLS", "SSL"]); self.security.SetStringSelection(value.security); self._row(grid, panel, "Security:", self.security)
        self.username = wx.TextCtrl(panel, value=value.username); self._row(grid, panel, "Username:", self.username)
        self.sender_address = wx.TextCtrl(panel, value=value.sender_address); self._row(grid, panel, "Sender email:", self.sender_address)
        self.sender_name = wx.TextCtrl(panel, value=value.sender_name); self._row(grid, panel, "Sender name:", self.sender_name)
        self.reply_to = wx.TextCtrl(panel, value=value.reply_to); self._row(grid, panel, "Reply-to (optional):", self.reply_to)
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.password.SetHint("Leave blank to keep the stored password")
        self._row(grid, panel, "New password:", self.password)
        outer.Add(grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.status = wx.StaticText(panel, label=self._credential_status())
        outer.Add(self.status, 0, wx.ALL, 12)
        if self.test_mode:
            warning = wx.StaticText(panel, label="TEST MODE: email delivery and connection tests are disabled.")
            warning.SetForegroundColour(wx.Colour(180, 35, 25)); outer.Add(warning, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        save = wx.Button(panel, label="Save Settings"); save.Bind(wx.EVT_BUTTON, self.on_save); actions.Add(save, 0, wx.RIGHT, 8)
        test = wx.Button(panel, label="Send Test Email..."); test.Enable(not self.test_mode); test.Bind(wx.EVT_BUTTON, self.on_test); actions.Add(test)
        actions.AddStretchSpacer(); close = wx.Button(panel, wx.ID_CLOSE, "Close"); close.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE)); actions.Add(close)
        outer.Add(actions, 0, wx.EXPAND | wx.ALL, 12); panel.SetSizer(outer)

    @staticmethod
    def _row(grid, panel, label, control):
        grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(control, 1, wx.EXPAND)

    def _credential_status(self):
        return "Protected password: {}".format("Stored" if self.factory.credentials.exists(CREDENTIAL_TARGET) else "Not stored")

    def _values(self):
        return ChurchMailSettings(
            self.enabled.GetValue(), self.server.GetValue().strip(), self.port.GetValue(),
            self.security.GetStringSelection(), self.username.GetValue().strip(),
            self.sender_address.GetValue().strip(), self.sender_name.GetValue().strip(),
            self.reply_to.GetValue().strip(), CREDENTIAL_TARGET, 30,
        )

    def on_save(self, _event):
        value = self._values()
        try:
            if value.enabled:
                JSForm.MailSettings(value.server, value.port, value.username or None,
                    "stored" if (self.password.GetValue() or self.factory.credentials.exists(CREDENTIAL_TARGET)) else None,
                    value.sender_address, value.sender_name, value.security.casefold(), value.reply_to or None).validate()
            if self.password.GetValue():
                self.factory.credentials.write(CREDENTIAL_TARGET, value.username, self.password.GetValue())
                self.password.SetValue("")
            self.repository.save(value); self.status.SetLabel(self._credential_status())
            wx.MessageBox("Email settings were saved.", "Email Settings", wx.OK | wx.ICON_INFORMATION, self)
        except Exception as error:
            wx.MessageBox(str(error), "Invalid Email Settings", wx.OK | wx.ICON_ERROR, self)

    def on_test(self, _event):
        address = wx.GetTextFromUser("Send a test message to:", "Test Email", self.sender_address.GetValue(), self)
        if not address: return
        if wx.MessageBox("Send one test email now?", "Confirm Test Email", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self) != wx.YES: return
        try:
            results = self.factory.build().send((address,), JSForm.MailMessage("ChurchManager email test", "ChurchManager email settings are working."))
            succeeded = bool(results and results[0].succeeded)
            status = "Succeeded" if succeeded else results[0].message
            self.repository.record_test(status)
            if not succeeded: raise RuntimeError(status)
            wx.MessageBox("The test email was sent.", "Email Test", wx.OK | wx.ICON_INFORMATION, self)
        except Exception as error:
            self.repository.record_test("Failed")
            wx.MessageBox(str(error), "Email Test Failed", wx.OK | wx.ICON_ERROR, self)


def show_mail_settings(parent, connection, authorization, test_mode=False):
    dialog = MailSettingsDialog(parent, connection, authorization, test_mode)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
