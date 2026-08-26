"""Authorized type-aware search for ChurchManager custom profile fields."""

from __future__ import annotations

import wx

from custom_profile_admin_dialog import _churches
from custom_profile_dialog import show_custom_profile
from custom_profile_fields import CustomProfileFieldService, CustomProfileValidationError
from custom_profile_repository import MariaDBCustomProfileRepository


OPERATIONS = {
    "SHORT_TEXT": (("Contains", "CONTAINS"), ("Starts with", "STARTS_WITH"), ("Equals", "EQUALS"), ("Is blank", "IS_BLANK"), ("Is not blank", "IS_NOT_BLANK")),
    "LONG_TEXT": (("Contains", "CONTAINS"), ("Starts with", "STARTS_WITH"), ("Equals", "EQUALS"), ("Is blank", "IS_BLANK"), ("Is not blank", "IS_NOT_BLANK")),
    "INTEGER": (("Equals", "EQUALS"), ("Less than", "LESS_THAN"), ("Greater than", "GREATER_THAN"), ("Range", "RANGE"), ("Is blank", "IS_BLANK")),
    "DECIMAL": (("Equals", "EQUALS"), ("Less than", "LESS_THAN"), ("Greater than", "GREATER_THAN"), ("Range", "RANGE"), ("Is blank", "IS_BLANK")),
    "DATE": (("Equals", "EQUALS"), ("Before", "LESS_THAN"), ("After", "GREATER_THAN"), ("Range", "RANGE"), ("Is blank", "IS_BLANK")),
    "BOOLEAN": (("Yes", "YES"), ("No", "NO"), ("Is blank", "IS_BLANK")),
    "SINGLE_CHOICE": (("Equals", "EQUALS"), ("Is blank", "IS_BLANK")),
    "MULTIPLE_CHOICE": (("Has any", "HAS_ANY"), ("Has all", "HAS_ALL"), ("Has none", "HAS_NONE")),
}


class CustomProfileSearchDialog(wx.Dialog):
    """Search approved custom fields and open a matching profile's extra data."""

    def __init__(self, parent, connection, session, authorization):
        super().__init__(parent, title="Custom Profile Search", size=(820, 570))
        self.connection = connection; self.session = session; self.authorization = authorization
        self.service = CustomProfileFieldService(MariaDBCustomProfileRepository(connection), session, authorization)
        self.church_rows = _churches(connection); self.definition_rows = []; self.result_rows = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        lead = wx.StaticText(panel, label="Search only active fields that an administrator explicitly approved for searching.")
        lead.SetForegroundColour(wx.Colour(0, 82, 170)); outer.Add(lead, 0, wx.ALL, 12)
        grid = wx.FlexGridSizer(cols=2, hgap=10, vgap=8); grid.AddGrowableCol(1, 1)
        self.church = wx.Choice(panel, choices=[row[1] for row in self.church_rows]); self.church.SetSelection(0 if self.church_rows else wx.NOT_FOUND)
        self.entity = wx.Choice(panel, choices=["People", "Families"]); self.entity.SetSelection(0)
        self.field = wx.Choice(panel); self.operation = wx.Choice(panel); self.value = wx.TextCtrl(panel)
        for label, control in (("Church", self.church), ("Profile type", self.entity), ("Field", self.field), ("Match", self.operation), ("Value", self.value)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        hint = wx.StaticText(panel, label="For ranges or multiple choices, separate values with commas. Dates use YYYY-MM-DD.")
        outer.Add(hint, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)
        self.choice_hint = wx.StaticText(panel, label="")
        outer.Add(self.choice_hint, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)
        search = wx.Button(panel, label="Search"); search.Bind(wx.EVT_BUTTON, self.on_search); outer.Add(search, 0, wx.LEFT | wx.TOP, 12)
        self.results = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.results.InsertColumn(0, "Name", width=420); self.results.InsertColumn(1, "Profile type", width=130); self.results.InsertColumn(2, "Record ID", width=100)
        self.results.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open)
        outer.Add(self.results, 1, wx.EXPAND | wx.ALL, 12)
        row = wx.BoxSizer(wx.HORIZONTAL); open_button = wx.Button(panel, label="Open Additional Information..."); open_button.Bind(wx.EVT_BUTTON, self.on_open)
        close = wx.Button(panel, wx.ID_CLOSE, "Close"); close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        row.Add(open_button); row.AddStretchSpacer(); row.Add(close); outer.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer)
        self.church.Bind(wx.EVT_CHOICE, self.load_fields); self.entity.Bind(wx.EVT_CHOICE, self.load_fields); self.field.Bind(wx.EVT_CHOICE, self.load_operations)
        self.operation.Bind(wx.EVT_CHOICE, self.update_value_state)
        self.load_fields(); self.CentreOnParent()

    def scope(self):
        return self.church_rows[self.church.GetSelection()][0], "PERSON" if self.entity.GetSelection() == 0 else "FAMILY"

    def load_fields(self, _event=None):
        self.definition_rows = [] if not self.church_rows else self.service.searchable_definitions(*self.scope())
        self.field.Set([row["label"] for row in self.definition_rows]); self.field.SetSelection(0 if self.definition_rows else wx.NOT_FOUND)
        self.load_operations()

    def load_operations(self, _event=None):
        selected = self.field.GetSelection()
        rows = () if selected < 0 else OPERATIONS[self.definition_rows[selected]["data_type"]]
        self.operation.Set([row[0] for row in rows]); self.operation.SetSelection(0 if rows else wx.NOT_FOUND)
        options = () if selected < 0 else self.service.repository.options(self.definition_rows[selected]["id"], active_only=True)
        self.choice_hint.SetLabel("Available choices: " + ", ".join(item["label"] for item in options) if options else "")
        self.update_value_state()

    def update_value_state(self, _event=None):
        field = self.field.GetSelection(); operation = self.operation.GetSelection()
        enabled = field >= 0 and operation >= 0 and OPERATIONS[self.definition_rows[field]["data_type"]][operation][1] not in {"IS_BLANK", "IS_NOT_BLANK", "YES", "NO"}
        self.value.Enable(enabled)

    def on_search(self, _event):
        selected = self.field.GetSelection(); operation = self.operation.GetSelection()
        if selected < 0 or operation < 0:
            wx.MessageBox("No searchable custom fields are available for this profile type.", "Custom Profile Search", wx.OK | wx.ICON_INFORMATION, self); return
        definition = self.definition_rows[selected]; operation_key = OPERATIONS[definition["data_type"]][operation][1]
        try: self.result_rows = self.service.search_profiles(*self.scope(), definition["id"], operation_key, self.value.GetValue())
        except (CustomProfileValidationError, ValueError) as error:
            wx.MessageBox(str(error), "Unable to Search", wx.OK | wx.ICON_ERROR, self); return
        self.results.DeleteAllItems()
        entity = "Person" if self.scope()[1] == "PERSON" else "Family"
        for item in self.result_rows:
            index = self.results.InsertItem(self.results.GetItemCount(), item["display_name"] or f"Record {item['id']}")
            self.results.SetItem(index, 1, entity); self.results.SetItem(index, 2, str(item["id"]))

    def on_open(self, _event):
        selected = self.results.GetFirstSelected()
        if selected < 0: return
        item = self.result_rows[selected]; church_id, entity = self.scope()
        show_custom_profile(self, self.connection, self.session, self.authorization, church_id, entity, item["id"], item["display_name"] or "Additional Information")


def show_custom_profile_search(parent, connection, session, authorization):
    """Open the authorized custom-profile search workflow."""
    dialog = CustomProfileSearchDialog(parent, connection, session, authorization)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()
