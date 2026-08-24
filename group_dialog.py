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


class AssignRoleDialog(wx.Dialog):
    """Collect a role and its effective start date."""

    def __init__(self, parent, roles):
        super().__init__(parent, title="Assign Group Role", size=(500, 190))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=10, hgap=12); grid.AddGrowableCol(1, 1)
        self.role = _choice(panel, roles); self.start = wx.adv.DatePickerCtrl(panel)
        for label, control in (("Role", self.role), ("Starts", self.start)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.ALL, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_OK, "Assign Role"), 0, wx.RIGHT, 8); buttons.Add(wx.Button(panel, wx.ID_CANCEL, "Cancel"))
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)

    def values(self):
        value = self.start.GetValue()
        return _selected_id(self.role), date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class NewCatalogItemDialog(wx.Dialog):
    """Collect one congregation-owned Group type or role."""

    def __init__(self, parent, kind):
        super().__init__(parent, title=f"New Group {kind.title()}", size=(520, 320))
        self.kind = kind; panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=9, hgap=12); grid.AddGrowableCol(1, 1)
        self.label = wx.TextCtrl(panel); self.key = wx.TextCtrl(panel); self.description = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        fields = [("Label", self.label), ("Stable key", self.key), ("Description", self.description)]
        self.special = wx.CheckBox(panel, label="Leadership role" if kind == "role" else "Restricted by default")
        fields.append(("Behavior", self.special))
        for label, control in fields:
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.ALL, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_OK, f"Create {kind.title()}"), 0, wx.RIGHT, 8); buttons.Add(wx.Button(panel, wx.ID_CANCEL, "Cancel"))
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)
        self.label.Bind(wx.EVT_TEXT, self._suggest_key)

    def _suggest_key(self, _event):
        if not self.key.IsModified(): self.key.ChangeValue(re.sub(r"[^a-z0-9]+", "-", self.label.GetValue().lower()).strip("-"))

    def values(self):
        return {"label": self.label.GetValue(), "item_key": self.key.GetValue(), "description": self.description.GetValue(),
                "privacy_class": "RESTRICTED" if self.kind == "type" and self.special.GetValue() else "STANDARD",
                "leadership_role": self.kind == "role" and self.special.GetValue()}


class GroupCatalogDialog(wx.Dialog):
    """Maintain local Group types or roles without deleting referenced history."""

    def __init__(self, parent, service, church_id, kind):
        super().__init__(parent, title=f"Group {kind.title()}s", size=(680, 480), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = service; self.church_id = church_id; self.kind = kind
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label=f"Maintain this congregation's Group {kind}s. Retired entries remain on historical records.")
        note.SetForegroundColour(wx.Colour(0, 82, 155)); outer.Add(note, 0, wx.ALL, 14)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Label", 190), ("Key", 170), ("Description", 230), ("Status", 70))): self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); self.add = wx.Button(panel, label=f"Add {kind.title()}..."); self.toggle = wx.Button(panel, label="Retire Selected")
        buttons.Add(self.add, 0, wx.RIGHT, 8); buttons.Add(self.toggle); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.add.Bind(wx.EVT_BUTTON, self.on_add); self.toggle.Bind(wx.EVT_BUTTON, self.on_toggle)
        self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE); self.refresh()

    def refresh(self):
        self.rows = self.service.catalog(self.church_id, self.kind); self.list.DeleteAllItems()
        for row in self.rows:
            index = self.list.InsertItem(self.list.GetItemCount(), row["label"])
            self.list.SetItem(index, 1, row["item_key"]); self.list.SetItem(index, 2, row.get("description") or "")
            self.list.SetItem(index, 3, "Active" if row["active"] else "Retired")

    def on_add(self, _event):
        dialog = NewCatalogItemDialog(self, self.kind)
        try:
            if dialog.ShowModal() == wx.ID_OK: self.service.create_catalog_item(self.church_id, self.kind, dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), f"Unable to Create {self.kind.title()}", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_toggle(self, _event):
        selected = self.list.GetFirstSelected()
        if selected < 0: return
        row = self.rows[selected]; self.service.set_catalog_active(self.kind, row["id"], not bool(row["active"])); self.refresh()


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
        for index, (label, width) in enumerate((("Person", 270), ("Roles", 180), ("Started", 105), ("Note", 210))): self.members.InsertColumn(index, label, width=width)
        outer.Add(self.members, 1, wx.EXPAND | wx.ALL, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); self.add = wx.Button(panel, label="Add Member...")
        self.assign = wx.Button(panel, label="Assign Role..."); self.end = wx.Button(panel, label="End Membership...")
        buttons.Add(self.add, 0, wx.RIGHT, 8); buttons.Add(self.assign, 0, wx.RIGHT, 8); buttons.Add(self.end)
        buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)
        self.add.Bind(wx.EVT_BUTTON, self.on_add); self.assign.Bind(wx.EVT_BUTTON, self.on_assign)
        self.end.Bind(wx.EVT_BUTTON, self.on_end); self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.refresh()

    def refresh(self):
        record = self.service.group(self.group_id)
        self.heading.SetLabel(record["name"])
        self.summary.SetLabel(f'{record["group_type"]} · {record["status"].title()} · {record["privacy_class"].title()}')
        self.members.DeleteAllItems()
        self.member_rows = self.service.memberships(self.group_id)
        for row in self.member_rows:
            index = self.members.InsertItem(self.members.GetItemCount(), row["person"])
            roles = ", ".join(item["role"] for item in self.service.membership_roles(row["id"]))
            self.members.SetItem(index, 1, roles or "Member"); self.members.SetItem(index, 2, _date_text(row["start_date"])); self.members.SetItem(index, 3, row.get("notes") or "")

    def on_add(self, _event):
        choices = self.service.choices(self.service.group(self.group_id)["church_id"])
        dialog = AddMemberDialog(self, choices["people"])
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            person_id, start, notes = dialog.values(); self.service.add_membership(self.group_id, person_id, start, notes=notes); self.refresh()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Add Member", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def _selected_membership(self):
        selected = self.members.GetFirstSelected()
        return self.member_rows[selected] if 0 <= selected < len(self.member_rows) else None

    def on_assign(self, _event):
        membership = self._selected_membership()
        if membership is None:
            wx.MessageBox("Select a member first.", "Assign Group Role", wx.OK | wx.ICON_INFORMATION, self); return
        group = self.service.group(self.group_id); roles = self.service.choices(group["church_id"])["roles"]
        dialog = AssignRoleDialog(self, roles)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            role_id, start = dialog.values(); self.service.assign_role(membership["id"], role_id, start); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Assign Role", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_end(self, _event):
        membership = self._selected_membership()
        if membership is None:
            wx.MessageBox("Select a member first.", "End Group Membership", wx.OK | wx.ICON_INFORMATION, self); return
        prompt = wx.TextEntryDialog(self, "Enter the last membership date (YYYY-MM-DD).", "End Group Membership", date.today().isoformat())
        try:
            if prompt.ShowModal() != wx.ID_OK: return
            end_date = date.fromisoformat(prompt.GetValue().strip())
            if wx.MessageBox(f'End {membership["person"]}\'s membership on {_date_text(end_date)}?', "Confirm End Membership", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES: return
            self.service.end_membership(membership["id"], end_date); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to End Membership", wx.OK | wx.ICON_ERROR, self)
        finally: prompt.Destroy()


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
        self.types = wx.Button(panel, label="Group Types..."); self.roles = wx.Button(panel, label="Group Roles...")
        buttons.Add(self.new, 0, wx.RIGHT, 8); buttons.Add(self.open, 0, wx.RIGHT, 16); buttons.Add(self.types, 0, wx.RIGHT, 8); buttons.Add(self.roles)
        buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.church.Bind(wx.EVT_CHOICE, self.refresh); self.status.Bind(wx.EVT_CHOICE, self.refresh)
        self.new.Bind(wx.EVT_BUTTON, self.on_new); self.open.Bind(wx.EVT_BUTTON, self.on_open); self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open)
        self.types.Bind(wx.EVT_BUTTON, lambda _event: self.open_catalog("type")); self.roles.Bind(wx.EVT_BUTTON, lambda _event: self.open_catalog("role"))
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

    def open_catalog(self, kind):
        church_id = _selected_id(self.church)
        if church_id is None: return
        try: dialog = GroupCatalogDialog(self, self.service, church_id, kind)
        except Exception as error:
            wx.MessageBox(str(error), "Group Catalog Unavailable", wx.OK | wx.ICON_ERROR, self); return
        try: dialog.ShowModal()
        finally: dialog.Destroy()


def show_groups(parent, connection, session, authorization):
    """Open the authorized Groups workspace modally."""
    dialog = GroupsDialog(parent, connection, session, authorization)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
