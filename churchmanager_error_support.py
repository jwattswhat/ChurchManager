"""ChurchManager integration for JSForm diagnostic error reporting."""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

import wx
import JSForm

from churchmanager_version import __version__


_SAFE_CONTEXT = {
    "application_mode": "unknown",
    "database_scope": "unknown",
    "authenticated": False,
}
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)


def _churchmanager_redactor(text: str) -> str:
    result = str(text)
    profile = os.environ.get("USERPROFILE")
    if profile:
        result = result.replace(profile, "[USERPROFILE]")
        result = result.replace(profile.replace("\\", "/"), "[USERPROFILE]")
    return _EMAIL.sub("[EMAIL]", result)


def configure_churchmanager_error_reporting():
    reporter = JSForm.configure_error_reporting(
        application_name="ChurchManager",
        application_version=__version__,
        error_id_prefix="CM",
        safe_context_provider=lambda: dict(_SAFE_CONTEXT),
        redactors=(_churchmanager_redactor,),
    )
    JSForm.install_error_hooks()
    return reporter


def update_runtime_context(arguments, session=None):
    database = str(arguments.get("database") or "unknown")
    is_test = bool(arguments.get("test_mode")) or database.casefold().endswith("test")
    _SAFE_CONTEXT.update({
        "application_mode": "test" if is_test else "production",
        "database_scope": "test" if is_test else "production",
        "database_name": database,
        "authenticated": session is not None,
    })


def safe_diagnostics():
    reporter = JSForm.current_error_reporter()
    return {
        "churchmanager_version": __version__,
        "jsform_version": reporter.config.jsform_version if reporter else None,
        "database_scope": _SAFE_CONTEXT.get("database_scope", "unknown"),
        "database_name": _SAFE_CONTEXT.get("database_name", "unknown"),
        "authenticated": bool(_SAFE_CONTEXT.get("authenticated")),
    }


class SupportDiagnosticsDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Support and Diagnostics", size=(610, 350))
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        reporter = JSForm.current_error_reporter()
        log_folder = reporter.log_directory if reporter else Path("Unavailable")

        heading = wx.StaticText(panel, label="ChurchManager Support and Diagnostics")
        font = heading.GetFont(); font.SetWeight(wx.FONTWEIGHT_BOLD); heading.SetFont(font)
        outer.Add(heading, 0, wx.ALL, 12)
        outer.Add(wx.StaticText(panel, label=f"Version: {__version__}"), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        outer.Add(wx.StaticText(panel, label=f"Diagnostic logs: {log_folder}"), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        explanation = wx.StaticText(panel, label=(
            "A support package contains diagnostic logs and safe version information. "
            "It does not contain database records, reports, attachments, images, email "
            "messages, or passwords. ChurchManager never sends it automatically."
        ))
        explanation.Wrap(560)
        outer.Add(explanation, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        create = wx.Button(panel, label="Create Support Package")
        open_folder = wx.Button(panel, label="Open Log Folder")
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        buttons.Add(create, 0, wx.RIGHT, 8)
        buttons.Add(open_folder, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer()
        buttons.Add(close)
        outer.AddStretchSpacer()
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(outer)

        create.Bind(wx.EVT_BUTTON, self.on_create)
        open_folder.Bind(wx.EVT_BUTTON, self.on_open_folder)
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))

    def on_create(self, _event):
        default_name = "ChurchManager-Support-{}.zip".format(datetime.now().strftime("%Y%m%d-%H%M%S"))
        default_folder = Path.home() / "Documents" / "ChurchManager" / "Support"
        default_folder.mkdir(parents=True, exist_ok=True)
        dialog = wx.FileDialog(
            self, "Save Support Package", defaultDir=str(default_folder),
            defaultFile=default_name, wildcard="ZIP files (*.zip)|*.zip",
            style=wx.FD_SAVE,
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            destination = Path(dialog.GetPath())
        finally:
            dialog.Destroy()
        try:
            JSForm.create_support_package(destination, safe_diagnostics=safe_diagnostics)
        except Exception as error:
            error_id = JSForm.report_exception(error, operation="support.package")
            JSForm.show_error_dialog(self, error_id, application_name="ChurchManager")
            return
        wx.MessageBox(
            "The support package was created. It has not been sent anywhere.\n\n{}".format(destination),
            "Support Package Created", wx.OK | wx.ICON_INFORMATION, self,
        )

    def on_open_folder(self, _event):
        reporter = JSForm.current_error_reporter()
        if not reporter:
            return
        reporter.log_directory.mkdir(parents=True, exist_ok=True)
        os.startfile(str(reporter.log_directory))


def show_support_diagnostics(parent):
    dialog = SupportDiagnosticsDialog(parent)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
