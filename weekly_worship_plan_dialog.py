"""Plan service-specific hymns and readings from a weekly bulletin order."""

from __future__ import annotations

import wx

from bulletin_orders import portable_connection


def suggestion_role_key(value):
    """Match full suggestion labels to the shorter template slot keys."""
    role = str(value or "").strip().casefold()
    if role == "communion" or role.startswith("distribution"):
        return "distribution hymn"
    return {
        "entrance": "hymn of invocation",
        "hymn of invocation": "hymn of invocation",
        "of the day": "hymn of the day",
        "hymn of the day": "hymn of the day",
    }.get(role, role)


class WeeklyWorshipPlanRepository:
    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def service(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT s.ChurchID,s.PropersID,s.DateTime,COALESCE(s.LiturgicalDate,'') "
                "FROM tblService s WHERE s.ID=?", (service_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("The selected Worship Service is unavailable.")
            return row
        finally:
            cursor.close()

    def hymn_slots(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT l.ID,l.ValueKey,COALESCE(h.Hymn,''),COALESCE(h.Title,'') "
                "FROM tblServiceBulletinOrderLine l "
                "LEFT JOIN tblHymnUsage u ON u.ServiceBulletinOrderLineID=l.ID "
                "LEFT JOIN tblHymn h ON h.ID=u.HymnID "
                "WHERE l.ServiceID=? AND l.Included=1 AND l.ValueSource='SERVICE_HYMN' "
                "ORDER BY l.Sequence,l.ID", (service_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def suggestions(self, propers_id):
        if not propers_id:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT s.HymnID,COALESCE(h.Hymn,''),COALESCE(h.Title,''),s.SuggestedAs "
                "FROM tblProperHymnSuggestion s JOIN tblHymn h ON h.ID=s.HymnID "
                "WHERE s.PropersID=? ORDER BY h.Hymn,h.Title,s.ID", (propers_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def hymn_catalog(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT ID,COALESCE(Hymn,''),COALESCE(Title,'') FROM tblHymn ORDER BY Hymn,Title")
            return cursor.fetchall()
        finally:
            cursor.close()

    def hymn_catalog_for_service(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT c.PrimaryHymnalID FROM tblService s "
                "LEFT JOIN tblChurch c ON c.ID=s.ChurchID WHERE s.ID=?", (service_id,),
            )
            row = cursor.fetchone()
            hymnal_id = row[0] if row else None
            if not hymnal_id:
                return self.hymn_catalog()
            cursor.execute(
                "SELECT ID,COALESCE(Hymn,''),COALESCE(Title,'') FROM tblHymn "
                "WHERE HymnalID=? ORDER BY Hymn,Title", (hymnal_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def set_hymn(self, service_id, line_id, used_as, hymn_id):
        church_id = self.service(service_id)[0]
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM tblHymnUsage WHERE ServiceID=? AND ServiceBulletinOrderLineID=?",
                (service_id, line_id),
            )
            weekly_value = None
            if hymn_id is not None:
                cursor.execute("SELECT COALESCE(Hymn,''),COALESCE(Title,'') FROM tblHymn WHERE ID=?", (hymn_id,))
                hymn = cursor.fetchone()
                weekly_value = " ".join(str(value) for value in hymn if value).strip()
                cursor.execute(
                    "INSERT INTO tblHymnUsage "
                    "(ChurchID,ServiceID,ServiceBulletinOrderLineID,HymnID,UsedAs) VALUES (?,?,?,?,?)",
                    (church_id, service_id, line_id, hymn_id, used_as),
                )
            cursor.execute(
                "UPDATE tblServiceBulletinOrderLine SET WeeklyValue=? WHERE ID=? AND ServiceID=?",
                (weekly_value, line_id, service_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def readings(self, service_id):
        propers_id = self.service(service_id)[1]
        cursor = self.connection.cursor()
        try:
            defaults = []
            if propers_id:
                cursor.execute(
                    "SELECT Reading,Reference FROM tblReading WHERE PropersID=? ORDER BY ID",
                    (propers_id,),
                )
                defaults = cursor.fetchall()
            return defaults
        finally:
            cursor.close()


class WeeklyWorshipPlanDialog(wx.Dialog):
    def __init__(self, parent, connection, service_id):
        super().__init__(parent, title="Plan Hymns and Readings", size=(880, 620),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = WeeklyWorshipPlanRepository(connection)
        self.service_id = service_id
        self.hymn_rows = []
        self.reading_rows = []
        self.catalog = self.repository.hymn_catalog_for_service(service_id)
        self.propers_id = self.repository.service(service_id)[1]
        self._build()
        self.refresh()
        self.CentreOnParent()

    def _build(self):
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label=(
            "Hymn selections belong to this Worship Service and remain in usage history. "
            "Lectionary readings are defaults; edit the corresponding weekly-order line to override one."
        ))
        note.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(note, 0, wx.ALL, 10)
        book = wx.Notebook(panel)
        hymn_page, reading_page = wx.Panel(book), wx.Panel(book)
        book.AddPage(hymn_page, "Hymns")
        book.AddPage(reading_page, "Readings")

        hymns = wx.BoxSizer(wx.VERTICAL)
        self.hymn_grid = wx.ListCtrl(hymn_page, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Position", 180), ("Hymn", 110), ("Title", 360), ("Suggested", 150)):
            self.hymn_grid.AppendColumn(label, width=width)
        hymns.Add(self.hymn_grid, 1, wx.EXPAND | wx.ALL, 8)
        hymn_buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("Select Hymn...", self.on_select_hymn), ("Clear Selection", self.on_clear_hymn)):
            button = wx.Button(hymn_page, label=label); button.Bind(wx.EVT_BUTTON, handler)
            hymn_buttons.Add(button, 0, wx.RIGHT, 8)
        hymns.Add(hymn_buttons, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        hymn_page.SetSizer(hymns)
        self.hymn_grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_select_hymn)

        readings = wx.BoxSizer(wx.VERTICAL)
        self.reading_grid = wx.ListCtrl(reading_page, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Reading", 190), ("Lectionary default", 520)):
            self.reading_grid.AppendColumn(label, width=width)
        readings.Add(self.reading_grid, 1, wx.EXPAND | wx.ALL, 8)
        reading_help = wx.StaticText(
            reading_page,
            label="To use a different reading, return to Weekly Order and double-click that reading line.",
        )
        readings.Add(reading_help, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        reading_page.SetSizer(readings)

        outer.Add(book, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_OK, "Apply to Weekly Order")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK))
        buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)

    def refresh(self):
        suggestions = self.repository.suggestions(self.propers_id)
        suggested_by_role = {}
        for _hymn_id, number, title, role in suggestions:
            suggested_by_role.setdefault(suggestion_role_key(role), []).append(
                " ".join(value for value in (str(number), title) if value).strip()
            )
        self.hymn_rows = self.repository.hymn_slots(self.service_id)
        self.hymn_grid.DeleteAllItems()
        for index, row in enumerate(self.hymn_rows):
            item = self.hymn_grid.InsertItem(index, str(row[1] or "Hymn"))
            self.hymn_grid.SetItem(item, 1, str(row[2]))
            self.hymn_grid.SetItem(item, 2, str(row[3]))
            matched = suggested_by_role.get(suggestion_role_key(row[1]), [])
            general = suggested_by_role.get("", [])
            self.hymn_grid.SetItem(item, 3, "; ".join(matched or general))
            if not row[2] and not row[3]:
                self.hymn_grid.SetItemTextColour(item, wx.RED)
        self.reading_rows = self.repository.readings(self.service_id)
        self.reading_grid.DeleteAllItems()
        for index, row in enumerate(self.reading_rows):
            item = self.reading_grid.InsertItem(index, str(row[0]))
            self.reading_grid.SetItem(item, 1, str(row[1] or ""))

    def _selected(self, grid, rows):
        index = grid.GetFirstSelected()
        return None if index < 0 else rows[index]

    def on_select_hymn(self, _event):
        row = self._selected(self.hymn_grid, self.hymn_rows)
        if not row:
            return
        choices = [" ".join(value for value in (str(item[1]), item[2]) if value).strip()
                   for item in self.catalog]
        dialog = wx.SingleChoiceDialog(self, f"Select the {row[1]}", "Select Hymn", choices)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.repository.set_hymn(
                    self.service_id, row[0], row[1], self.catalog[dialog.GetSelection()][0]
                )
                self.refresh()
        finally:
            dialog.Destroy()

    def on_clear_hymn(self, _event):
        row = self._selected(self.hymn_grid, self.hymn_rows)
        if row:
            self.repository.set_hymn(self.service_id, row[0], row[1], None); self.refresh()

def show_weekly_worship_plan(parent, connection, service_id):
    dialog = WeeklyWorshipPlanDialog(parent, connection, service_id)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
