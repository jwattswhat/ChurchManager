"""ChurchManager login and initial master-administrator dialogs."""

from __future__ import annotations

import wx

from authentication import (
    AuthenticationError, AuthenticationService, MariaDBUserRepository,
    PasswordService,
)


class _CredentialDialog(wx.Dialog):
    def add_field(self, sizer, label, style=0, value=""):
        sizer.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
        control = wx.TextCtrl(self, value=value, style=style, size=(280, -1))
        sizer.Add(control, 1, wx.EXPAND)
        return control

    def finish(self, fields):
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(fields, 1, wx.ALL | wx.EXPAND, 16)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 12)
        self.SetSizerAndFit(root)
        self.CentreOnScreen()


class LoginDialog(_CredentialDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="ChurchManager Login")
        fields = wx.FlexGridSizer(2, 2, 10, 10)
        fields.AddGrowableCol(1, 1)
        self.username = self.add_field(fields, "Username")
        self.password = self.add_field(fields, "Password", wx.TE_PASSWORD)
        self.finish(fields)
        self.username.SetFocus()


class InitialMasterDialog(_CredentialDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="Create Initial Master Administrator")
        fields = wx.FlexGridSizer(4, 2, 10, 10)
        fields.AddGrowableCol(1, 1)
        self.username = self.add_field(fields, "Username", value="jonathan")
        self.display_name = self.add_field(
            fields, "Display name", value="Rev. Jonathan C. Watt"
        )
        self.password = self.add_field(fields, "Password", wx.TE_PASSWORD)
        self.confirmation = self.add_field(fields, "Confirm password", wx.TE_PASSWORD)
        self.finish(fields)


class ChangePasswordDialog(_CredentialDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="Change ChurchManager Password")
        fields = wx.FlexGridSizer(2, 2, 10, 10)
        fields.AddGrowableCol(1, 1)
        self.password = self.add_field(fields, "New password", wx.TE_PASSWORD)
        self.confirmation = self.add_field(fields, "Confirm password", wx.TE_PASSWORD)
        self.finish(fields)


class ChangeOwnPasswordDialog(_CredentialDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="Change ChurchManager Password")
        fields = wx.FlexGridSizer(3, 2, 10, 10)
        fields.AddGrowableCol(1, 1)
        self.current = self.add_field(fields, "Current password", wx.TE_PASSWORD)
        self.password = self.add_field(fields, "New password", wx.TE_PASSWORD)
        self.confirmation = self.add_field(fields, "Confirm password", wx.TE_PASSWORD)
        self.finish(fields)


def _message(parent, text, title, style=wx.OK | wx.ICON_ERROR):
    dialog = wx.MessageDialog(parent, text, title, style)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()


def ensure_initial_master(repository, passwords, parent=None):
    if repository.has_users():
        return True
    while True:
        dialog = InitialMasterDialog(parent)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return False
            username = dialog.username.GetValue().strip()
            display_name = dialog.display_name.GetValue().strip()
            password = dialog.password.GetValue()
            confirmation = dialog.confirmation.GetValue()
        finally:
            dialog.Destroy()
        if not username or not display_name:
            _message(parent, "Username and display name are required.", "Initial setup")
            continue
        if password != confirmation:
            _message(parent, "The passwords do not match.", "Initial setup")
            continue
        try:
            password_hash = passwords.hash(password)
            repository.create_initial_master(username, display_name, password_hash)
            return True
        except (ValueError, RuntimeError) as error:
            _message(parent, str(error), "Initial setup")


def require_password_change(repository, passwords, session, parent=None):
    if not session.must_change_password:
        return True
    while True:
        dialog = ChangePasswordDialog(parent)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return False
            password = dialog.password.GetValue()
            confirmation = dialog.confirmation.GetValue()
        finally:
            dialog.Destroy()
        if password != confirmation:
            _message(parent, "The passwords do not match.", "Change password")
            continue
        try:
            repository.change_password(session.user_id, passwords.hash(password))
            return True
        except (ValueError, RuntimeError) as error:
            _message(parent, str(error), "Change password")


def change_own_password(connection, session, parent=None, minimum_length=12):
    """Change the signed-in user's password after verifying the current one."""
    repository = MariaDBUserRepository(connection)
    passwords = PasswordService(minimum_length=minimum_length)
    dialog = ChangeOwnPasswordDialog(parent)
    try:
        if dialog.ShowModal() != wx.ID_OK:
            return False
        current = dialog.current.GetValue()
        password = dialog.password.GetValue()
        confirmation = dialog.confirmation.GetValue()
    finally:
        dialog.Destroy()
    account = repository.find_by_username(session.username)
    if account is None or not passwords.verify(account.password_hash, current):
        _message(parent, "The current password is incorrect.", "Change password")
        return False
    if password != confirmation:
        _message(parent, "The new passwords do not match.", "Change password")
        return False
    try:
        repository.change_password(session.user_id, passwords.hash(password))
    except (ValueError, RuntimeError) as error:
        _message(parent, str(error), "Change password")
        return False
    _message(
        parent, "Your ChurchManager password has been changed.",
        "Change password", wx.OK | wx.ICON_INFORMATION,
    )
    return True


def authenticate_user(connection, parent=None, minimum_length=12):
    """Run initial setup if needed, then return an authenticated session or None."""
    repository = MariaDBUserRepository(connection)
    passwords = PasswordService(minimum_length=minimum_length)
    if not ensure_initial_master(repository, passwords, parent):
        return None
    service = AuthenticationService(repository, passwords)
    while True:
        dialog = LoginDialog(parent)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return None
            username = dialog.username.GetValue()
            password = dialog.password.GetValue()
        finally:
            dialog.Destroy()
        try:
            session = service.authenticate(username, password)
        except AuthenticationError as error:
            _message(parent, str(error), "Login failed")
            continue
        if not require_password_change(repository, passwords, session, parent):
            return None
        return session
