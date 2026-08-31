"""Installed ChurchManager entry point with guarded first-run setup."""

from __future__ import annotations

import argparse
from churchmanager_mode import load_config
from configuration_paths import ensure_configuration
from installed_package_check import package_check
from installation_readiness import find_mariadb_tool


def database_startup_message(error):
    """Return an actionable message for an expected local database failure."""

    chain = []
    current = error
    while current is not None and current not in chain:
        chain.append(current)
        current = current.__cause__ or current.__context__
    details = "\n".join(str(item) for item in chain).casefold()
    database_failure = any(marker in details for marker in (
        "database connection could not be established",
        "can't connect to mysql server",
        "connection refused",
        "winerror 10061",
        "access denied for user",
        "auth_gssapi_client",
    ))
    if not database_failure:
        return None
    if not (find_mariadb_tool("mariadb.exe") or find_mariadb_tool("mysql.exe")):
        return (
            "MariaDB Server is not installed yet.\n\n"
            "Install MariaDB Server for Windows, then run ChurchManager "
            "Installation again.\n\n"
            "Download MariaDB Server: https://mariadb.org/download/"
        )
    if "auth_gssapi_client" in details or "access denied for user" in details:
        return (
            "ChurchManager could not sign in to MariaDB. The saved database "
            "account or password does not match this MariaDB installation.\n\n"
            "Run ChurchManager Installation again to configure the local database."
        )
    return (
        "ChurchManager could not reach MariaDB. Confirm that the MariaDB Windows "
        "service is running, then try again."
    )


def show_database_startup_message(message):
    """Display one nontechnical installed-startup database message."""

    import wx
    import wx.adv

    owns_application = wx.App.Get() is None
    application = wx.App(False) if owns_application else wx.App.Get()
    dialog = wx.Dialog(None, title="ChurchManager Needs MariaDB")
    outer = wx.BoxSizer(wx.VERTICAL)
    display_message = message.replace(
        "\n\nDownload MariaDB Server: https://mariadb.org/download/", ""
    )
    text = wx.StaticText(dialog, label=display_message)
    text.Wrap(460)
    outer.Add(text, 0, wx.ALL | wx.EXPAND, 16)
    if "https://mariadb.org/download/" in message:
        outer.Add(
            wx.adv.HyperlinkCtrl(
                dialog, label="Download MariaDB Server",
                url="https://mariadb.org/download/",
            ),
            0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 16,
        )
    button = wx.Button(dialog, wx.ID_OK, "OK")
    outer.Add(button, 0, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.BOTTOM, 16)
    dialog.SetSizerAndFit(outer)
    dialog.SetMinSize((520, dialog.GetSize().height))
    dialog.CentreOnScreen()
    dialog.ShowModal()
    dialog.Destroy()
    if owns_application:
        application.Destroy()


def setup_required(config=None):
    """Return whether the installed production connection is not configured."""

    config = config or load_config()
    values = config.get("database_settings", {})
    return not (
        config.get("security", {}).get("production_enabled")
        and str(values.get("user") or "").strip()
        and str(values.get("database") or "").strip()
    )


def main(argv=None):
    """Run protected setup when needed, then open ordinary ChurchManager."""

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--setup", action="store_true")
    parser.add_argument("--package-check")
    known, remaining = parser.parse_known_args(argv)
    if known.package_check:
        return package_check(known.package_check)
    ensure_configuration()
    test_mode = "--test" in remaining
    if known.setup or (setup_required() and not test_mode):
        from installed_setup import main as run_setup
        run_setup()
    if setup_required() and not test_mode:
        return 0
    from cm import main as run_churchmanager
    try:
        return run_churchmanager(remaining)
    except Exception as error:
        message = database_startup_message(error)
        if message is None:
            raise
        show_database_startup_message(message)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
