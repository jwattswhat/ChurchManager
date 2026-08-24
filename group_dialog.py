"""Native Groups workspace for identity and current membership management."""

from __future__ import annotations

from datetime import date
import re

import wx
import wx.adv

from group_repository import MariaDBGroupRepository
from group_service import GroupService, GroupValidationError


def _choice(parent, rows):
    control = wx.Choice(parent, choices=[str(row[1]) for row in rows])
    control.rows = list(rows)
    if rows:
        control.SetSelection(0)
    return control


def _selected_id(control):
    selection = control.GetSelection()
    return control.rows[selection][0] if 0 <= selection < len(control.rows) else None


def _date_text(value):
    return value.strftime("%m/%d/%Y") if value else ""


class NewGroupDialog(wx.Dialog):
    """Collect the minimum fields required for a new Group."""

    def __init__(self, parent, church_id, choices):
        super().__init__(parent, title="New Group", size=(560, 470))
        self.church_id = church_id
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        guidance = wx.StaticText(panel, label="Create a congregational Group. Membership is added after the Group is saved.")
        guidance.SetForegroundColour(wx.Colour(0, 82, 155)); outer.Add(guidance, 0, wx.ALL, 14)
        grid = wx.FlexGridSizer(cols=2, vgap=9, hgap=12); grid.AddGrowableCol(1, 1)
        self.name = wx.TextCtrl(panel); self.key = wx.TextCtrl(panel)
        self.group_type = _choice(panel, choices["types"])
        self.status = wx.Choice(panel, choices=["Draft", "Active", "Inactive"]); self.status.SetSelection(1)
        self.privacy = wx.Choice(panel, choices=["Standard", "Restricted"]); self.privacy.SetSelection(0)
        self.description = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        for label, control in (("Name", self.name), ("Group key", self.key), ("Type", self.group_type),
                               ("Status", self.status), ("Privacy", self.privacy), ("Description", self.description)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_OK, "Create Group"), 0, wx.RIGHT, 8)
        buttons.Add(wx.Button(panel, wx.ID_CANCEL, "Cancel"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.name.Bind(wx.EVT_TEXT, self._suggest_key)

    def _suggest_key(self, _event):
        if not self.key.IsModified():
            key = re.sub(r"[^a-z0-9]+", "-", self.name.GetValue().lower()).strip("-")
            self.key.ChangeValue(key)

    def values(self):
        return {"church_id": self.church_id, "name": self.name.GetValue(), "group_key": self.key.GetValue(),
                "group_type_id": _selected_id(self.group_type), "status": self.status.GetStringSelection().upper(),
                "privacy_class": self.privacy.GetStringSelection().upper(),
                "description": self.description.GetValue()}


class AddMemberDialog(wx.Dialog):
    """Collect one dated membership term."""

    def __init__(self, parent, people):
        super().__init__(parent, title="Add Group Member", size=(520, 250))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=10, hgap=12); grid.AddGrowableCol(1, 1)
        self.person = _choice(panel, people)
        self.start = wx.adv.DatePickerCtrl(panel)
        self.notes = wx.TextCtrl(panel)
        for label, control in (("Person", self.person), ("Starts", self.start), ("Note (optional)", self.notes)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.ALL, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_OK, "Add Member"), 0, wx.RIGHT, 8); buttons.Add(wx.Button(panel, wx.ID_CANCEL, "Cancel"))
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)

    def values(self):
        value = self.start.GetValue()
        return _selected_id(self.person), date(value.GetYear(), value.GetMonth() + 1, value.GetDay()), self.notes.GetValue()


class GroupDetailDialog(wx.Dialog):
    """Show Group identity and its current authorized roster."""

    def __init__(self, parent, service, group_id):
        super().__init__(parent, title="Group", size=(820, 560), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = service; self.group_id = group_id
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        self.heading = wx.StaticText(panel); font = self.heading.GetFont(); font.MakeBold(); font.SetPointSize(font.GetPointSize() + 2); self.heading.SetFont(font)
        self.summary = wx.StaticText(panel)
        outer.Add(self.heading, 0, wx.ALL, 14); outer.Add(self.summary, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        outer.Add(wx.StaticText(panel, label="Current members"), 0, wx.LEFT | wx.RIGHT, 14)
        self.members = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Person", 330), ("Started", 110), ("Note", 280))): self.members.InsertColumn(index, label, width=width)
        outer.Add(self.members, 1, wx.EXPAND | wx.ALL, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); self.add = wx.Button(panel, label="Add Member...")
        buttons.Add(self.add); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)
        self.add.Bind(wx.EVT_BUTTON, self.on_add); self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.refresh()

    def refresh(self):
        record = self.service.group(self.group_id)
        self.heading.SetLabel(record["name"])
        self.summary.SetLabel(f'{record["group_type"]} · {record["status"].title()} · {record["privacy_class"].title()}')
        self.members.DeleteAllItems()
        for row in self.service.memberships(self.group_id):
            index = self.members.InsertItem(self.members.GetItemCount(), row["person"])
            self.members.SetItem(index, 1, _date_text(row["start_date"])); self.members.SetItem(index, 2, row.get("notes") or "")

    def on_add(self, _event):
        choices = self.service.choices(self.service.group(self.group_id)["church_id"])
        dialog = AddMemberDialog(self, choices["people"])
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            person_id, start, notes = dialog.values(); self.service.add_membership(self.group_id, person_id, start, notes=notes); self.refresh()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Add Member", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()


class GroupsDialog(wx.Dialog):
    """List visible Groups and open their current membership workspace."""

    def __init__(self, parent, connection, session, authorization):
        super().__init__(parent, title="Groups", size=(900, 600), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = MariaDBGroupRepository(connection); self.service = GroupService(self.repository, session, authorization)
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label="Congregational Groups"); font = title.GetFont(); font.MakeBold(); font.SetPointSize(font.GetPointSize() + 2); title.SetFont(font)
        outer.Add(title, 0, wx.ALL, 14)
        filters = wx.BoxSizer(wx.HORIZONTAL); filters.Add(wx.StaticText(panel, label="Church"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.church = _choice(panel, self.repository.churches()); filters.Add(self.church, 1, wx.RIGHT, 12)
        filters.Add(wx.StaticText(panel, label="Status"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.status = wx.Choice(panel, choices=["All", "Draft", "Active", "Inactive", "Closed"]); self.status.SetSelection(0); filters.Add(self.status)
        outer.Add(filters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Group", 300), ("Type", 200), ("Status", 100), ("Members", 90), ("Privacy", 110))): self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); self.new = wx.Button(panel, label="New Group..."); self.open = wx.Button(panel, label="Open Group")
        buttons.Add(self.new, 0, wx.RIGHT, 8); buttons.Add(self.open); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.church.Bind(wx.EVT_CHOICE, self.refresh); self.status.Bind(wx.EVT_CHOICE, self.refresh)
        self.new.Bind(wx.EVT_BUTTON, self.on_new); self.open.Bind(wx.EVT_BUTTON, self.on_open); self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open)
        self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE); self.refresh()

    def refresh(self, _event=None):
        church_id = _selected_id(self.church); status = self.status.GetStringSelection().upper()
        rows = self.service.list_groups(church_id, None if status == "ALL" else status) if church_id else []
        self.rows = rows; self.list.DeleteAllItems()
        for row in rows:
            index = self.list.InsertItem(self.list.GetItemCount(), row["name"])
            for column, value in enumerate((row["group_type"], row["status"].title(), str(row["current_members"]), row["privacy_class"].title()), 1): self.list.SetItem(index, column, value)

    def on_new(self, _event):
        church_id = _selected_id(self.church); dialog = NewGroupDialog(self, church_id, self.service.choices(church_id))
        try:
            if dialog.ShowModal() == wx.ID_OK: self.service.create_group(dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Create Group", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_open(self, _event):
        selected = self.list.GetFirstSelected()
        if selected < 0: return
        dialog = GroupDetailDialog(self, self.service, self.rows[selected]["id"])
        try: dialog.ShowModal()
        finally: dialog.Destroy(); self.refresh()


def show_groups(parent, connection, session, authorization):
    """Open the authorized Groups workspace modally."""
    dialog = GroupsDialog(parent, connection, session, authorization)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
