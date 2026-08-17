"""Administrative package manager for versioned lectionary metadata."""

from __future__ import annotations

from pathlib import Path
import wx

from bulletin_orders import portable_connection
from lectionary_importer import LectionaryPackageImporter
from lectionary_packages import LectionaryPackageValidator, load_lectionary_package


class LectionaryPackageRepository:
    """Read installed package summaries without exposing package internals."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def installed(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT PackageCode,Title,PackageVersion,SourceName,InstalledAt,IsActive "
                "FROM tblLectionaryPackage ORDER BY Title,PackageCode"
            )
            return cursor.fetchall()
        finally:
            cursor.close()


class LectionaryPackageDialog(wx.Dialog):
    """Preview and explicitly install checksum-protected lectionary packages."""

    def __init__(self, parent, connection, authorization):
        authorization.require(
            "application.config.manage", operation="Manage lectionary packages",
        )
        super().__init__(
            parent, title="Lectionary Packages", size=(980, 620),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.connection = connection
        self.repository = LectionaryPackageRepository(connection)
        self.package = None
        self.checksum = None
        self.path = None
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(
            panel,
            label="Packages contain reference metadata only. Select a file to validate and preview it before installation.",
        )
        note.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(note, 0, wx.ALL, 10)
        outer.Add(wx.StaticText(panel, label="Installed packages"), 0, wx.LEFT | wx.RIGHT, 10)
        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (
            ("Package", 170), ("Title", 260), ("Version", 100),
            ("Source", 220), ("Installed", 140), ("Active", 70),
        ):
            self.grid.AppendColumn(label, width=width)
        outer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 10)
        preview_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Selected package preview")
        self.preview = wx.StaticText(panel, label="No package file selected.")
        preview_box.Add(self.preview, 0, wx.EXPAND | wx.ALL, 8)
        outer.Add(preview_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        choose = wx.Button(panel, label="Choose Package...")
        choose.Bind(wx.EVT_BUTTON, self.on_choose)
        actions.Add(choose, 0, wx.RIGHT, 8)
        self.install_button = wx.Button(panel, label="Install / Upgrade")
        self.install_button.Enable(False)
        self.install_button.Bind(wx.EVT_BUTTON, self.on_install)
        actions.Add(self.install_button, 0, wx.RIGHT, 8)
        actions.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        actions.Add(close)
        outer.Add(actions, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)
        self.refresh()
        self.CentreOnParent()

    def refresh(self):
        """Reload installed package summaries."""
        self.grid.DeleteAllItems()
        for index, row in enumerate(self.repository.installed()):
            self.grid.InsertItem(index, str(row[0]))
            for column, value in enumerate(row[1:], 1):
                if column == 5:
                    value = "Yes" if value else "No"
                self.grid.SetItem(index, column, str(value or ""))

    def on_choose(self, _event):
        dialog = wx.FileDialog(
            self, "Choose Lectionary Package", wildcard="JSON package (*.json)|*.json",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path = Path(dialog.GetPath())
        finally:
            dialog.Destroy()
        try:
            package, checksum = load_lectionary_package(path)
            summary = LectionaryPackageValidator().validate(package, checksum)
        except Exception as error:
            self.package = self.checksum = self.path = None
            self.install_button.Enable(False)
            wx.MessageBox(str(error), "Invalid Lectionary Package", wx.OK | wx.ICON_ERROR, self)
            return
        self.package, self.checksum, self.path = package, checksum, path
        self.preview.SetLabel(
            f"{package['title']}  |  Version {summary.package_version}\n"
            f"Source: {package['source_name']} — {package['source_reference']}\n"
            f"{summary.system_count} system(s), {summary.edition_count} edition(s), "
            f"{summary.cycle_count} cycle(s), {summary.proper_count} Propers, "
            f"{summary.appointment_count} reading appointment(s)\n"
            f"Notice: {package['package_notice']}"
        )
        self.install_button.Enable(True)
        self.Layout()

    def on_install(self, _event):
        if self.package is None:
            return
        if wx.MessageBox(
            f"Install or upgrade '{self.package['title']}' from the validated package?",
            "Confirm Lectionary Package", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        ) != wx.YES:
            return
        try:
            result = LectionaryPackageImporter(self.connection).install(
                self.package, self.checksum,
            )
        except Exception as error:
            wx.MessageBox(str(error), "Package Installation Failed", wx.OK | wx.ICON_ERROR, self)
            return
        self.refresh()
        self.install_button.Enable(False)
        wx.MessageBox(
            f"Package {result.package_code} {result.package_version} was installed successfully.",
            "Lectionary Package", wx.OK | wx.ICON_INFORMATION, self,
        )


def show_lectionary_packages(parent, connection, authorization):
    """Open the protected lectionary package manager."""
    dialog = LectionaryPackageDialog(parent, connection, authorization)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
