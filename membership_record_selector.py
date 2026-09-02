"""Searchable record selection before opening People and Families forms."""

from __future__ import annotations

from dataclasses import dataclass

import wx


@dataclass(frozen=True)
class MembershipRecordChoice:
    """One person or family offered by the membership record selector."""

    record_id: int
    label: str


def filter_choices(choices, search_text):
    """Return choices whose labels contain all typed words, case-insensitively."""
    words = search_text.casefold().split()
    if not words:
        return list(choices)
    return [
        choice for choice in choices
        if all(word in choice.label.casefold() for word in words)
    ]


def distinguish_duplicate_labels(choices):
    """Add a record number only when identical names need disambiguation."""
    counts = {}
    for choice in choices:
        key = choice.label.casefold()
        counts[key] = counts.get(key, 0) + 1
    return [
        MembershipRecordChoice(
            choice.record_id,
            "{} (record {})".format(choice.label, choice.record_id)
            if counts[choice.label.casefold()] > 1 else choice.label,
        )
        for choice in choices
    ]


def resolve_typed_choice(choices, typed_text):
    """Resolve an exact label or the sole partial match to one record choice."""
    typed = typed_text.strip().casefold()
    if not typed:
        return None
    for choice in choices:
        if choice.label.casefold() == typed:
            return choice
    matches = filter_choices(choices, typed_text)
    return matches[0] if len(matches) == 1 else None


class MembershipRecordRepository:
    """Read the names used to select an existing person or family."""

    def __init__(self, connection):
        self.connection = connection

    def choices(self, entity_type):
        """Return all existing records in the edit form's navigation order."""
        if entity_type == "person":
            sql = (
                "SELECT ID, FirstName, MiddleName, LastName FROM tblPerson "
                "ORDER BY LastName, FirstName, MiddleName, ID"
            )
        elif entity_type == "family":
            sql = "SELECT ID, FamilyName FROM tblFamily ORDER BY FamilyName, ID"
        else:
            raise ValueError("The membership selector supports person or family records.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
        finally:
            cursor.close()
        if entity_type == "person":
            return distinguish_duplicate_labels([
                MembershipRecordChoice(row[0], self._person_label(*row[1:]))
                for row in rows
            ])
        return distinguish_duplicate_labels([
            MembershipRecordChoice(row[0], str(row[1] or "Unnamed family"))
            for row in rows
        ])

    @staticmethod
    def _person_label(first_name, middle_name, last_name):
        given = " ".join(
            str(value).strip() for value in (first_name, middle_name) if value
        )
        family = str(last_name or "").strip()
        if family and given:
            return "{}, {}".format(family, given)
        return family or given or "Unnamed person"


class MembershipRecordSelectorDialog(wx.Dialog):
    """Let the user type a name and choose a matching membership record."""

    def __init__(self, parent, entity_type, choices):
        noun = "Person" if entity_type == "person" else "Family"
        super().__init__(
            parent, title="Select {}".format(noun), size=(640, 235),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.SetMinSize((560, 225))
        self.all_choices = list(choices)
        self.visible_choices = list(self.all_choices)
        self.selected_record_id = None

        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(
            wx.StaticText(
                panel,
                label="Type a name, then choose the {} to edit.".format(noun.lower()),
            ),
            0, wx.ALL, 14,
        )
        self.name = wx.ComboBox(
            panel, choices=[choice.label for choice in self.visible_choices],
            style=wx.CB_DROPDOWN,
        )
        if hasattr(self.name, "AutoComplete"):
            self.name.AutoComplete([choice.label for choice in self.all_choices])
        outer.Add(self.name, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        self.no_matches = wx.StaticText(panel, label="No matching records.")
        self.no_matches.SetForegroundColour(wx.Colour(160, 0, 0))
        self.no_matches.Hide()
        outer.Add(self.no_matches, 0, wx.LEFT | wx.RIGHT | wx.TOP, 14)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.new_button = wx.Button(panel, wx.ID_ADD, "New {}...".format(noun))
        self.open_button = wx.Button(panel, wx.ID_OK, "Open")
        self.cancel_button = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        buttons.Add(self.new_button, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer()
        buttons.Add(self.open_button, 0, wx.RIGHT, 8)
        buttons.Add(self.cancel_button)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14)
        panel.SetSizer(outer)

        self.name.Bind(wx.EVT_TEXT, self._on_text)
        self.name.Bind(wx.EVT_COMBOBOX, self._on_selection)
        self.new_button.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_ADD))
        self.open_button.Bind(wx.EVT_BUTTON, self._on_open)
        self.open_button.Enable(False)
        self.name.SetFocus()

    def _on_text(self, _event):
        typed = self.name.GetValue()
        self.visible_choices = filter_choices(self.all_choices, typed)
        resolved = resolve_typed_choice(self.all_choices, typed)
        self.selected_record_id = resolved.record_id if resolved else None
        self.open_button.Enable(resolved is not None)
        self.no_matches.Show(not self.visible_choices)
        self.Layout()

    def _on_selection(self, _event):
        resolved = resolve_typed_choice(self.all_choices, self.name.GetValue())
        if resolved is not None:
            self.selected_record_id = resolved.record_id
            self.open_button.Enable(True)

    def _on_open(self, _event):
        resolved = resolve_typed_choice(self.all_choices, self.name.GetValue())
        if resolved is not None:
            self.selected_record_id = resolved.record_id
            self.EndModal(wx.ID_OK)


def position_form_at_record(form, record_id):
    """Position an already-loaded JSForm form without narrowing its record set."""
    records = getattr(form, "RECORDS", None)
    loaded = getattr(records, "_record", None) or []
    for index, record in enumerate(loaded):
        if record.get("ID") == record_id:
            records._select(index)
            form.fill_form(records.current())
            if getattr(form, "NavControlsPresent", False):
                form.enable_navigation_buttons()
            return True
    return False


def select_and_open_membership_record(parent, connection, form_factory, entity_type):
    """Select a record and open its full, normally navigable edit form."""
    choices = MembershipRecordRepository(connection).choices(entity_type)
    noun = "person" if entity_type == "person" else "family"
    dialog = MembershipRecordSelectorDialog(parent, entity_type, choices)
    try:
        result = dialog.ShowModal()
        if result not in {wx.ID_OK, wx.ID_ADD}:
            return None
        record_id = dialog.selected_record_id
    finally:
        dialog.Destroy()
    form_name = "frmPerson" if entity_type == "person" else "frmFamily"
    form = form_factory.create(form_name)
    if result == wx.ID_ADD:
        form.new_record()
        form.show()
        return form
    if not position_form_at_record(form, record_id):
        form.FRAME.Destroy()
        wx.MessageBox(
            "That {} record is no longer available.".format(noun),
            "Record Not Found", wx.OK | wx.ICON_WARNING, parent,
        )
        return None
    form.show()
    return form
