"""Fast Worship Service picker that opens one service record at a time."""

from __future__ import annotations

import wx

from unified_worship_service_dialog import (
    UnifiedWorshipServiceRepository,
    show_unified_worship_service,
)


SERVICE_FIELDS = [
    "ID", "ChurchID", "DateTime", "Location", "PropersID", "LiturgicalDate",
    "HolyCommunion", "BulletinOrderTemplateID", "OSNote",
    "SermonID", "Bulletin", "CheckListComplete", "Note",
]


class WorshipServiceDialog(wx.Dialog):
    def __init__(self, parent, connection, form_factory, session=None):
        super().__init__(
            parent, title="Worship Services", size=(900, 570),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.connection = connection
        self.form_factory = form_factory
        self.session = session
        # JSForm child windows detach themselves from both registries when they
        # close. This picker is deliberately lightweight, but still honors that
        # parent contract.
        self.LINKEDFORM = {}
        self.SUBFORM = {}
        self.rows = []
        self._build()
        self.refresh()
        self.CentreOnParent()

    def _build(self):
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        help_text = wx.StaticText(
            panel,
            label=(
                "Double-click a service to continue its preparation. The Weekly Order column "
                "shows whether its service-specific outline has been created."
            ),
        )
        help_text.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(help_text, 0, wx.ALL, 10)
        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (
            ("Date and time", 165), ("Liturgical date", 230), ("Location", 150),
            ("Communion", 90), ("Weekly order", 210),
        ):
            self.grid.AppendColumn(label, width=width)
        outer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (
            ("New Service", self.on_new),
            ("Open Service", self.on_open),
            ("Delete Service", self.on_delete),
        ):
            button = wx.Button(panel, label=label)
            button.Bind(wx.EVT_BUTTON, handler)
            buttons.Add(button, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open)

    def refresh(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT s.ID,s.DateTime,COALESCE(s.LiturgicalDate,''),"
                "COALESCE(s.Location,''),s.HolyCommunion,"
                "COALESCE(t.Name,'Not created') "
                "FROM tblService s "
                "LEFT JOIN tblServiceBulletinOrder w ON w.ServiceID=s.ID "
                "LEFT JOIN tblBulletinOrderTemplate t ON t.ID=w.TemplateID "
                "ORDER BY s.DateTime DESC,s.ID DESC"
            )
            self.rows = cursor.fetchall()
        finally:
            cursor.close()
        self.grid.DeleteAllItems()
        for index, row in enumerate(self.rows):
            when = row[1].strftime("%m/%d/%Y %I:%M %p") if hasattr(row[1], "strftime") else str(row[1])
            item = self.grid.InsertItem(index, when)
            values = (row[2], row[3], "Yes" if row[4] else "No", row[5])
            for column, value in enumerate(values, 1):
                self.grid.SetItem(item, column, str(value))
            if row[5] == "Not created":
                self.grid.SetItemTextColour(item, wx.RED)

    def _open_editor(self, service_id=None, new=False):
        if service_id is not None and not new:
            show_unified_worship_service(self, self.connection, service_id)
            self.refresh()
            return
        repository = UnifiedWorshipServiceRepository(self.connection)
        churches = repository.churches()
        if not churches:
            wx.MessageBox("Create a Church record before adding a Worship Service.",
                          "Church Required", wx.OK | wx.ICON_WARNING, self)
            return
        church_id = churches[0][0]
        if len(churches) > 1:
            chooser = wx.SingleChoiceDialog(
                self, "Select the church for this service.", "New Worship Service",
                [str(row[1]) for row in churches],
            )
            try:
                if chooser.ShowModal() != wx.ID_OK:
                    return
                church_id = churches[chooser.GetSelection()][0]
            finally:
                chooser.Destroy()
        new_id = repository.create_service(church_id)
        saved = False
        try:
            saved = show_unified_worship_service(
                self, self.connection, new_id, new_service=True,
            )
        finally:
            if not saved:
                repository.discard_unsaved_service(new_id)
        self.refresh()

    def _on_editor_close(self, event):
        event.Skip()
        wx.CallAfter(self.refresh)

    def on_new(self, _event):
        self._open_editor(new=True)

    def on_open(self, _event):
        selected = self.grid.GetFirstSelected()
        if selected >= 0:
            self._open_editor(self.rows[selected][0])

    def on_delete(self, _event):
        selected = self.grid.GetFirstSelected()
        if selected < 0:
            wx.MessageBox("Select a service to delete.", "Delete Worship Service",
                          wx.OK | wx.ICON_INFORMATION, self)
            return
        row = self.rows[selected]
        when = row[1].strftime("%m/%d/%Y %I:%M %p") if hasattr(row[1], "strftime") else str(row[1])
        title = str(row[2] or "Untitled service")
        message = (
            f"Delete this Worship Service?\n\n{when}\n{title}\n\n"
            "Its weekly Order of Service and hymn selections will also be deleted. "
            "Services with attendance or participant assignments are protected."
        )
        if wx.MessageBox(message, "Delete Worship Service",
                         wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES:
            return
        try:
            UnifiedWorshipServiceRepository(self.connection).delete_service(
                row[0], self.session,
            )
            self.refresh()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Delete Worship Service",
                          wx.OK | wx.ICON_WARNING, self)


def show_worship_services(parent, connection, form_factory, session=None):
    dialog = WorshipServiceDialog(parent, connection, form_factory, session)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
