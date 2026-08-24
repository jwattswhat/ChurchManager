"""Administrative catalog screens for church-defined profile fields and tags."""

from __future__ import annotations

import wx

from custom_profile_fields import CustomProfileFieldService, CustomProfileValidationError
from custom_profile_repository import MariaDBCustomProfileRepository


def _churches(connection):
    cursor = connection.cursor()
    marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
    try:
        cursor.execute("SELECT ID,Church FROM tblChurch WHERE ID>0 ORDER BY Church")
        return cursor.fetchall()
    finally:
        cursor.close()


class NewFieldDialog(wx.Dialog):
    """Collect the intentionally small immutable core of a new custom field."""

    TYPES = (
        ("Short text", "SHORT_TEXT"), ("Long text", "LONG_TEXT"),
        ("Whole number", "INTEGER"), ("Decimal number", "DECIMAL"),
        ("Date", "DATE"), ("Yes / No", "BOOLEAN"),
        ("Single choice", "SINGLE_CHOICE"), ("Multiple choice", "MULTIPLE_CHOICE"),
    )

    def __init__(self, parent):
        super().__init__(parent, title="New Custom Profile Field", size=(500, 510))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, hgap=10, vgap=8); grid.AddGrowableCol(1, 1)
        self.controls = {}
        for key, label, control in (
            ("label", "Label", wx.TextCtrl(panel)),
            ("field_key", "Stable key", wx.TextCtrl(panel)),
            ("section_label", "Section", wx.TextCtrl(panel, value="Additional Information")),
            ("data_type", "Field type", wx.Choice(panel, choices=[item[0] for item in self.TYPES])),
            ("privacy_class", "Privacy", wx.Choice(panel, choices=["Standard", "Restricted"])),
            ("help_text", "Help text", wx.TextCtrl(panel)),
        ):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND); self.controls[key] = control
        self.controls["data_type"].SetSelection(0); self.controls["privacy_class"].SetSelection(0)
        outer.Add(grid, 0, wx.EXPAND | wx.ALL, 14)
        self.confirm = wx.CheckBox(panel, label="I confirm this field will not duplicate protected, prohibited, or existing core information.")
        outer.Add(self.confirm, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        buttons = wx.StdDialogButtonSizer(); buttons.AddButton(wx.Button(panel, wx.ID_OK, "Create Draft")); buttons.AddButton(wx.Button(panel, wx.ID_CANCEL)); buttons.Realize()
        outer.Add(buttons, 0, wx.ALIGN_RIGHT | wx.ALL, 14); panel.SetSizer(outer); self.CentreOnParent()

    def values(self):
        return {
            "label": self.controls["label"].GetValue(), "field_key": self.controls["field_key"].GetValue(),
            "section_label": self.controls["section_label"].GetValue(),
            "data_type": self.TYPES[self.controls["data_type"].GetSelection()][1],
            "privacy_class": "RESTRICTED" if self.controls["privacy_class"].GetSelection() == 1 else "STANDARD",
            "help_text": self.controls["help_text"].GetValue(),
            "content_boundary_confirmed": self.confirm.GetValue(),
        }


class CustomProfileAdministrationDialog(wx.Dialog):
    """Maintain custom field definitions, choice catalogs, and profile tags."""

    def __init__(self, parent, connection, session, authorization):
        super().__init__(parent, title="Custom Profile Fields and Tags", size=(900, 640))
        self.service = CustomProfileFieldService(MariaDBCustomProfileRepository(connection), session, authorization)
        self.churches = _churches(connection); self.field_rows = []; self.tag_rows = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        lead = wx.StaticText(panel, label="Define bounded additional information for People and Families. Draft fields must be activated before use.")
        lead.SetForegroundColour(wx.Colour(0, 82, 170)); outer.Add(lead, 0, wx.ALL, 12)
        selectors = wx.BoxSizer(wx.HORIZONTAL)
        selectors.Add(wx.StaticText(panel, label="Church"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.church = wx.Choice(panel, choices=[item[1] for item in self.churches]); self.church.SetSelection(0 if self.churches else wx.NOT_FOUND)
        selectors.Add(self.church, 1, wx.RIGHT, 16)
        selectors.Add(wx.StaticText(panel, label="Profile type"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.entity = wx.Choice(panel, choices=["Person", "Family"]); self.entity.SetSelection(0); selectors.Add(self.entity, 0)
        outer.Add(selectors, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.tabs = wx.Notebook(panel); self._build_fields_tab(); self._build_tags_tab()
        outer.Add(self.tabs, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        close = wx.Button(panel, wx.ID_CLOSE, "Close"); close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        outer.Add(close, 0, wx.ALIGN_RIGHT | wx.ALL, 12); panel.SetSizer(outer)
        self.church.Bind(wx.EVT_CHOICE, self.refresh); self.entity.Bind(wx.EVT_CHOICE, self.refresh)
        self.refresh(); self.CentreOnParent()

    def _build_fields_tab(self):
        panel = wx.Panel(self.tabs); outer = wx.BoxSizer(wx.VERTICAL)
        self.fields = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (name, width) in enumerate((("Field", 220), ("Type", 140), ("Section", 190), ("Privacy", 100), ("Status", 90))): self.fields.InsertColumn(index, name, width=width)
        outer.Add(self.fields, 1, wx.EXPAND | wx.ALL, 8)
        row = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("New Field...", self.new_field), ("Add Choice...", self.add_choice), ("Activate", self.activate), ("Retire", self.retire)):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler); row.Add(button, 0, wx.RIGHT, 8)
        outer.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8); panel.SetSizer(outer); self.tabs.AddPage(panel, "Custom Fields")

    def _build_tags_tab(self):
        panel = wx.Panel(self.tabs); outer = wx.BoxSizer(wx.VERTICAL)
        self.tags = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (name, width) in enumerate((("Tag", 250), ("Key", 180), ("Privacy", 120), ("Status", 100))): self.tags.InsertColumn(index, name, width=width)
        outer.Add(self.tags, 1, wx.EXPAND | wx.ALL, 8)
        row = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("New Tag...", self.new_tag), ("Activate", lambda e: self.tag_active(True)), ("Retire", lambda e: self.tag_active(False))):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler); row.Add(button, 0, wx.RIGHT, 8)
        outer.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8); panel.SetSizer(outer); self.tabs.AddPage(panel, "Tags")

    def scope(self):
        return self.churches[self.church.GetSelection()][0], "PERSON" if self.entity.GetSelection() == 0 else "FAMILY"

    def refresh(self, _event=None):
        if not self.churches: return
        church_id, entity = self.scope()
        try:
            self.field_rows = self.service.definitions(church_id, entity, include_drafts=True)
            self.tag_rows = self.service.tag_catalog(church_id, entity)
        except PermissionError as error:
            wx.MessageBox(str(error), "Custom Profiles", wx.OK | wx.ICON_ERROR, self); return
        self.fields.DeleteAllItems()
        for item in self.field_rows:
            index = self.fields.InsertItem(self.fields.GetItemCount(), item["label"])
            for column, value in enumerate((item["data_type"].replace("_", " ").title(), item["section_label"], item["privacy_class"].title(), item["lifecycle_status"].title()), 1): self.fields.SetItem(index, column, value)
        self.tags.DeleteAllItems()
        for item in self.tag_rows:
            index = self.tags.InsertItem(self.tags.GetItemCount(), item["label"])
            for column, value in enumerate((item["tag_key"], item["privacy_class"].title(), "Active" if item["active"] else "Retired"), 1): self.tags.SetItem(index, column, value)

    def selected_field(self):
        index = self.fields.GetFirstSelected(); return None if index < 0 else self.field_rows[index]

    def new_field(self, _event):
        dialog = NewFieldDialog(self)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            values = dialog.values(); values.update(zip(("church_id", "entity_type"), self.scope()))
            self.service.create_definition(values); self.refresh()
        except (CustomProfileValidationError, ValueError) as error: wx.MessageBox(str(error), "Unable to Create Field", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def add_choice(self, _event):
        item = self.selected_field()
        if not item: return
        key = wx.GetTextFromUser("Stable lowercase option key", "Add Choice", parent=self)
        if not key: return
        label = wx.GetTextFromUser("Choice label", "Add Choice", parent=self)
        if not label: return
        try: self.service.add_option(item["id"], key, label); self.refresh()
        except (CustomProfileValidationError, ValueError) as error: wx.MessageBox(str(error), "Unable to Add Choice", wx.OK | wx.ICON_ERROR, self)

    def activate(self, _event): self._field_status(True)
    def retire(self, _event): self._field_status(False)
    def _field_status(self, active):
        item = self.selected_field()
        if not item: return
        try:
            (self.service.activate_definition if active else self.service.retire_definition)(item["id"]); self.refresh()
        except (CustomProfileValidationError, ValueError) as error: wx.MessageBox(str(error), "Unable to Change Field", wx.OK | wx.ICON_ERROR, self)

    def new_tag(self, _event):
        label = wx.GetTextFromUser("Tag label", "New Profile Tag", parent=self)
        if not label: return
        key = wx.GetTextFromUser("Stable lowercase tag key", "New Profile Tag", parent=self)
        if not key: return
        church_id, entity = self.scope()
        try: self.service.create_tag({"church_id": church_id, "entity_type": entity, "tag_key": key, "label": label}); self.refresh()
        except (CustomProfileValidationError, ValueError) as error: wx.MessageBox(str(error), "Unable to Create Tag", wx.OK | wx.ICON_ERROR, self)

    def tag_active(self, active):
        index = self.tags.GetFirstSelected()
        if index < 0: return
        try: self.service.set_tag_active(self.tag_rows[index]["id"], active); self.refresh()
        except (CustomProfileValidationError, ValueError) as error: wx.MessageBox(str(error), "Unable to Change Tag", wx.OK | wx.ICON_ERROR, self)


def show_custom_profile_administration(parent, connection, session, authorization):
    """Open the authenticated custom-profile administration catalog."""
    dialog = CustomProfileAdministrationDialog(parent, connection, session, authorization)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()
