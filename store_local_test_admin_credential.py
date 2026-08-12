"""Securely store the local MariaDB administrator credential."""
import wx
from credential_store import write_credential

TARGET = "ChurchManager/LocalTestAdmin"

def main():
    app = wx.App(False)
    dialog = wx.PasswordEntryDialog(
        None,
        "Enter the password for the local MariaDB church account.",
        "Local MariaDB Credential",
    )
    try:
        if dialog.ShowModal() != wx.ID_OK:
            return 2
        password = dialog.GetValue()
        if not password:
            wx.MessageBox("No password was entered.", "Credential not stored")
            return 2
        write_credential(TARGET, "church", password)
        wx.MessageBox(
            "The local MariaDB credential was stored securely.",
            "Credential stored",
            wx.OK | wx.ICON_INFORMATION,
        )
        return 0
    finally:
        dialog.Destroy()

if __name__ == "__main__":
    raise SystemExit(main())
