"""Securely store the local MariaDB restore-administrator credential."""
import wx

from credential_store import write_credential


TARGET = "ChurchManager/LocalRestoreAdmin"


def main():
    app = wx.App(False)
    dialog = wx.PasswordEntryDialog(
        None,
        "Enter the new password for the local MariaDB root account.",
        "New Local MariaDB Root Password",
    )
    confirm = None
    try:
        if dialog.ShowModal() != wx.ID_OK:
            return 2
        password = dialog.GetValue()
        if not password:
            wx.MessageBox("No password was entered.", "Credential not stored")
            return 2
        confirm = wx.PasswordEntryDialog(
            None,
            "Enter the new MariaDB root password again.",
            "Confirm MariaDB Root Password",
        )
        if confirm.ShowModal() != wx.ID_OK:
            return 2
        if confirm.GetValue() != password:
            wx.MessageBox("The passwords did not match.", "Credential not stored")
            return 2
        write_credential(TARGET, "root", password)
        wx.MessageBox(
            "The local restore-administrator credential was stored securely.",
            "Credential stored",
            wx.OK | wx.ICON_INFORMATION,
        )
        return 0
    finally:
        if confirm is not None:
            confirm.Destroy()
        dialog.Destroy()


if __name__ == "__main__":
    raise SystemExit(main())
