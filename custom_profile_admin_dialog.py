"""Administrative catalog screens for church-defined profile fields and tags."""

from __future__ import annotations

import wx

from custom_profile_fields import CustomProfileFieldService, CustomProfileValidationError
from custom_profile_exchange import CustomProfileExchangeService
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
        policies = wx.BoxSizer(wx.HORIZONTAL)
        for key, label in (("searchable", "Allow search"), ("report_allowed", "Allow approved reports"), ("export_allowed", "Allow approved exports")):
            control = wx.CheckBox(panel, label=label); self.controls[key] = control
            policies.Add(control, 0, wx.RIGHT, 16)
        outer.Add(policies, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
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
            "searchable": self.controls["searchable"].GetValue(),
            "report_allowed": self.controls["report_allowed"].GetValue(),
            "export_allowed": self.controls["export_allowed"].GetValue(),
            "content_boundary_confirmed": self.confirm.GetValue(),
        }


class FieldDetailsDialog(wx.Dialog):
    """Display the complete definition and permit lifecycle-safe edits."""

    TYPES = NewFieldDialog.TYPES

    def __init__(self, parent, service, definition):
        super().__init__(parent, title="Custom Field Definition", size=(650, 690))
        self.service = service; self.definition = definition; self.controls = {}
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        status = definition["lifecycle_status"]
        messages = {
            "DRAFT": "Draft - all definition settings may be edited before activation.",
            "ACTIVE": "Active - labels and usage policies may be edited; structural settings are locked.",
            "RETIRED": "Retired - this historical definition is read-only.",
        }
        heading = wx.StaticText(panel, label=messages[status]); heading.SetForegroundColour(wx.Colour(0, 82, 170))
        outer.Add(heading, 0, wx.EXPAND | wx.ALL, 12)
        identity = wx.StaticText(panel, label=(
            f"Definition ID: {definition['id']}    Church ID: {definition['church_id']}    "
            f"Profile: {definition['entity_type'].title()}    Version: {definition['version']}"
        ))
        outer.Add(identity, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        grid = wx.FlexGridSizer(cols=2, hgap=10, vgap=7); grid.AddGrowableCol(1, 1)
        type_labels = [item[0] for item in self.TYPES]; type_values = [item[1] for item in self.TYPES]
        controls = (
            ("label", "Label", wx.TextCtrl(panel, value=str(definition["label"] or ""))),
            ("field_key", "Stable key", wx.TextCtrl(panel, value=str(definition["field_key"] or ""))),
            ("section_label", "Section", wx.TextCtrl(panel, value=str(definition["section_label"] or ""))),
            ("data_type", "Field type", wx.Choice(panel, choices=type_labels)),
            ("privacy_class", "Privacy", wx.Choice(panel, choices=["Standard", "Restricted"])),
            ("display_order", "Display order", wx.SpinCtrl(panel, min=0, max=9999, initial=int(definition["display_order"] or 0))),
            ("max_length", "Maximum length", wx.TextCtrl(panel, value="" if definition["max_length"] is None else str(definition["max_length"]))),
            ("minimum_value", "Minimum value", wx.TextCtrl(panel, value="" if definition["minimum_value"] is None else str(definition["minimum_value"]))),
            ("maximum_value", "Maximum value", wx.TextCtrl(panel, value="" if definition["maximum_value"] is None else str(definition["maximum_value"]))),
            ("decimal_places", "Decimal places", wx.SpinCtrl(panel, min=0, max=6, initial=int(definition["decimal_places"] or 0))),
            ("help_text", "Help text", wx.TextCtrl(panel, value=str(definition["help_text"] or ""), style=wx.TE_MULTILINE, size=(-1, 75))),
        )
        for key, label, control in controls:
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND); self.controls[key] = control
        self.controls["data_type"].SetSelection(type_values.index(definition["data_type"]))
        self.controls["privacy_class"].SetSelection(1 if definition["privacy_class"] == "RESTRICTED" else 0)
        outer.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        policies = wx.StaticBoxSizer(wx.StaticBox(panel, label="Usage policies"), wx.HORIZONTAL)
        for key, label in (("required", "Required"), ("searchable", "Searchable"),
                           ("report_allowed", "Approved reports"), ("export_allowed", "Approved exports")):
            control = wx.CheckBox(panel, label=label); control.SetValue(bool(definition[key])); self.controls[key] = control
            policies.Add(control, 0, wx.ALL, 8)
        outer.Add(policies, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        options = service.repository.options(definition["id"], active_only=False)
        option_text = ", ".join(f"{item['label']} ({item['option_key']})" for item in options) or "None"
        outer.Add(wx.StaticText(panel, label="Choices: " + option_text), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        buttons = wx.StdDialogButtonSizer()
        if status != "RETIRED": buttons.AddButton(wx.Button(panel, wx.ID_OK, "Save Changes"))
        buttons.AddButton(wx.Button(panel, wx.ID_CANCEL, "Close")); buttons.Realize()
        outer.Add(buttons, 0, wx.ALIGN_RIGHT | wx.ALL, 12); panel.SetSizer(outer)
        if status != "DRAFT":
            for key in ("field_key", "data_type", "privacy_class", "max_length", "minimum_value", "maximum_value", "decimal_places"):
                self.controls[key].Enable(False)
        if status == "RETIRED":
            for control in self.controls.values(): control.Enable(False)
        self.CentreOnParent()

    def values(self):
        values = {}
        for key in ("label", "field_key", "section_label", "help_text", "max_length", "minimum_value", "maximum_value"):
            values[key] = self.controls[key].GetValue()
        values.update({
            "church_id": self.definition["church_id"], "entity_type": self.definition["entity_type"],
            "data_type": self.TYPES[self.controls["data_type"].GetSelection()][1],
            "privacy_class": "RESTRICTED" if self.controls["privacy_class"].GetSelection() == 1 else "STANDARD",
            "display_order": self.controls["display_order"].GetValue(),
            "decimal_places": self.controls["decimal_places"].GetValue(),
        })
        for key in ("required", "searchable", "report_allowed", "export_allowed"):
            values[key] = self.controls[key].GetValue()
        return values


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
        for label, handler in (("New Field...", self.new_field), ("Open Field...", self.open_field), ("Add Choice...", self.add_choice), ("Activate", self.activate), ("Retire", self.retire), ("Export Values...", self.export_values), ("Import Values...", self.import_values)):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler); row.Add(button, 0, wx.RIGHT, 8)
        self.fields.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.open_field)
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

    def open_field(self, _event):
        item = self.selected_field()
        if not item: return
        dialog = FieldDetailsDialog(self, self.service, item)
        try:
            if item["lifecycle_status"] != "RETIRED" and dialog.ShowModal() == wx.ID_OK:
                self.service.update_definition(item["id"], dialog.values()); self.refresh()
            elif item["lifecycle_status"] == "RETIRED": dialog.ShowModal()
        except (CustomProfileValidationError, ValueError, RuntimeError) as error:
            wx.MessageBox(str(error), "Unable to Update Field", wx.OK | wx.ICON_ERROR, self)
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

    def export_values(self, _event):
        dialog = CustomProfileExportDialog(self, CustomProfileExchangeService(self.service), *self.scope())
        try: dialog.ShowModal()
        finally: dialog.Destroy()

    def import_values(self, _event):
        dialog = CustomProfileImportDialog(self, CustomProfileExchangeService(self.service), *self.scope())
        try: dialog.ShowModal()
        finally: dialog.Destroy()

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


class CustomProfileExportDialog(wx.Dialog):
    """Confirm an explicit stable-key custom-value export."""

    def __init__(self, parent, service, church_id, entity_type):
        super().__init__(parent, title="Export Custom Profile Values", size=(610, 300))
        self.service = service; self.church_id = church_id; self.entity_type = entity_type
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label=(
            "This separate export contains only Active custom fields marked for approved export. "
            "A metadata manifest records stable field and choice keys."
        )); note.Wrap(560); note.SetForegroundColour(wx.Colour(0, 82, 170)); outer.Add(note, 0, wx.EXPAND | wx.ALL, 14)
        self.restricted = wx.CheckBox(panel, label="Include authorized Restricted custom values")
        self.restricted.Enable(service.authorization.has_permission("profiles.custom_fields.view_restricted"))
        outer.Add(self.restricted, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        warning = wx.StaticText(panel, label="Restricted exports require a separate explicit selection and must be handled securely.")
        outer.Add(warning, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        row = wx.BoxSizer(wx.HORIZONTAL); export = wx.Button(panel, label="Choose File and Export..."); close = wx.Button(panel, wx.ID_CANCEL, "Close")
        export.Bind(wx.EVT_BUTTON, self.on_export); row.Add(export, 0, wx.RIGHT, 8); row.Add(close)
        outer.AddStretchSpacer(); outer.Add(row, 0, wx.ALIGN_RIGHT | wx.ALL, 14); panel.SetSizer(outer); self.CentreOnParent()

    def on_export(self, _event):
        if self.restricted.GetValue() and wx.MessageBox(
            "Include Restricted custom values in this export?\n\nThe destination must be protected.",
            "Confirm Restricted Export", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        ) != wx.YES: return
        dialog = wx.FileDialog(self, "Save custom profile values", wildcard="CSV files (*.csv)|*.csv",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            count, manifest = self.service.export(self.church_id, self.entity_type, dialog.GetPath(), self.restricted.GetValue())
            wx.MessageBox(f"Exported {count} profile row(s).\nMetadata: {manifest.name}", "Custom Profile Export Complete", wx.OK | wx.ICON_INFORMATION, self)
        except (CustomProfileValidationError, PermissionError, OSError, ValueError) as error:
            wx.MessageBox(str(error), "Unable to Export Custom Profiles", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()


class CustomProfileImportDialog(wx.Dialog):
    """Preview and atomically import stable-key values for existing profiles."""

    def __init__(self, parent, service, church_id, entity_type):
        super().__init__(parent, title="Import Custom Profile Values", size=(820, 590))
        self.service = service; self.church_id = church_id; self.entity_type = entity_type
        self.source = None; self.preview = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label=(
            "Choose a stable-key custom-profile CSV. Preview makes no database changes. "
            "Imports update existing matching profiles and never create fields, choices, People, or Families."
        )); note.Wrap(770); note.SetForegroundColour(wx.Colour(0, 82, 170)); outer.Add(note, 0, wx.EXPAND | wx.ALL, 12)
        choose = wx.Button(panel, label="Choose CSV and Preview..."); choose.Bind(wx.EVT_BUTTON, self.on_choose)
        outer.Add(choose, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.rows = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("CSV row", 80), ("Profile", 300), ("Fields", 90), ("Status", 290))): self.rows.InsertColumn(index, label, width=width)
        outer.Add(self.rows, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.status = wx.StaticText(panel, label="Choose a CSV file to begin."); outer.Add(self.status, 0, wx.EXPAND | wx.ALL, 12)
        buttons = wx.BoxSizer(wx.HORIZONTAL); self.commit = wx.Button(panel, label="Import All Ready Rows"); self.commit.Enable(False)
        self.commit.Bind(wx.EVT_BUTTON, self.on_commit); close = wx.Button(panel, wx.ID_CANCEL, "Close")
        buttons.Add(self.commit, 0, wx.RIGHT, 8); buttons.Add(close); outer.Add(buttons, 0, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer); self.CentreOnParent()

    def on_choose(self, _event):
        dialog = wx.FileDialog(self, "Choose custom profile CSV", wildcard="CSV files (*.csv)|*.csv")
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            self.source = dialog.GetPath(); self.preview = self.service.preview_import(self.church_id, self.entity_type, self.source)
            self._show_preview()
        except (CustomProfileValidationError, PermissionError, OSError, ValueError) as error:
            self.preview = []; self.commit.Enable(False)
            wx.MessageBox(str(error), "Unable to Preview Custom Profiles", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def _show_preview(self):
        self.rows.DeleteAllItems(); error_count = 0
        for item in self.preview:
            status = "; ".join(item.errors) if item.errors else "Ready"
            index = self.rows.InsertItem(self.rows.GetItemCount(), str(item.row_number))
            self.rows.SetItem(index, 1, item.display_name); self.rows.SetItem(index, 2, str(len(item.changes))); self.rows.SetItem(index, 3, status)
            if item.errors:
                error_count += 1; self.rows.SetItemTextColour(index, wx.Colour(190, 0, 0))
        ready = len(self.preview) - error_count
        self.status.SetLabel(f"Previewed {len(self.preview)} row(s): {ready} Ready, {error_count} need attention. No database records were changed.")
        self.commit.Enable(bool(self.preview) and not error_count)

    def on_commit(self, _event):
        if not self.preview or not self.source: return
        if wx.MessageBox(
            f"Import custom values for all {len(self.preview)} reviewed profile row(s)?",
            "Confirm Custom Profile Import", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        ) != wx.YES: return
        try:
            count = self.service.commit_import(self.church_id, self.entity_type, self.source, self.preview)
            wx.MessageBox(f"Imported custom values for {count} profile row(s).", "Custom Profile Import Complete", wx.OK | wx.ICON_INFORMATION, self)
            self.commit.Enable(False); self.status.SetLabel("Import complete. Close this window or preview another file.")
        except (CustomProfileValidationError, PermissionError, OSError, ValueError, RuntimeError) as error:
            wx.MessageBox(str(error), "Unable to Import Custom Profiles", wx.OK | wx.ICON_ERROR, self)


def show_custom_profile_administration(parent, connection, session, authorization):
    """Open the authenticated custom-profile administration catalog."""
    dialog = CustomProfileAdministrationDialog(parent, connection, session, authorization)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()
