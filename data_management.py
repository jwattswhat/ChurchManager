"""Safe duplicate review foundation for ChurchManager data management."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import csv
from pathlib import Path
import re
import unicodedata

import wx

from bulletin_orders import portable_connection


def normalized_text(value):
    """Return conservative comparison text without presentation punctuation."""
    text = unicodedata.normalize("NFKC", str(value or "")).casefold().strip()
    return " ".join(re.findall(r"[\w]+", text, flags=re.UNICODE))


def normalized_contact(value):
    """Normalize an email or telephone value for exact duplicate comparison."""
    text = str(value or "").strip().casefold()
    if "@" in text:
        return text
    return "".join(character for character in text if character.isdigit())


@dataclass(frozen=True)
class DuplicateCandidate:
    """A read-only possible duplicate pair shown for human review."""

    entity: str
    first_id: int
    first_name: str
    second_id: int
    second_name: str
    reason: str


def duplicate_pairs(records, key, entity, reason):
    """Return unique record pairs sharing a nonblank normalized key."""
    grouped = defaultdict(list)
    for record in records:
        value = key(record)
        if value:
            grouped[value].append(record)
    found = []
    for rows in grouped.values():
        for index, first in enumerate(rows):
            for second in rows[index + 1:]:
                if first[0] != second[0]:
                    found.append(DuplicateCandidate(
                        entity, int(first[0]), first[1], int(second[0]), second[1], reason,
                    ))
    return found


CSV_FIELDS = {
    "People": (
        ("First name", "FirstName", True),
        ("Middle name", "MiddleName", False),
        ("Last name", "LastName", True),
        ("Suffix", "Suffix", False),
        ("Email", "Email", False),
        ("Phone", "Phone", False),
    ),
    "Families": (
        ("Family name", "FamilyName", True),
        ("Address", "Address", False),
        ("Address line 2", "Address2", False),
        ("City", "City", False),
        ("State", "State", False),
        ("ZIP", "Zip", False),
        ("Email", "Email", False),
        ("Phone", "Phone", False),
    ),
}


def read_csv_rows(path):
    """Read a UTF-8 CSV into headers and rows without changing application data."""
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = [str(value or "").strip() for value in (reader.fieldnames or [])]
        if not headers or any(not value for value in headers):
            raise ValueError("The CSV must have a nonblank header row.")
        if len({normalized_text(value) for value in headers}) != len(headers):
            raise ValueError("The CSV contains duplicate column names.")
        rows = [{header: str(row.get(header) or "").strip() for header in headers} for row in reader]
    if not rows:
        raise ValueError("The CSV contains no data rows.")
    return headers, rows


def suggested_csv_mapping(headers, entity):
    """Suggest conservative header mappings; the user must still review them."""
    aliases = {
        "FirstName": ("first name", "firstname", "given name"),
        "MiddleName": ("middle name", "middlename"),
        "LastName": ("last name", "lastname", "surname", "family name"),
        "Suffix": ("suffix",), "FamilyName": ("family name", "familyname", "household"),
        "Address": ("address", "address 1", "street"),
        "Address2": ("address 2", "address line 2"), "City": ("city",),
        "State": ("state", "province"), "Zip": ("zip", "zipcode", "postal code"),
        "Email": ("email", "e mail"), "Phone": ("phone", "telephone", "mobile"),
    }
    normalized = {normalized_text(header): header for header in headers}
    mapping = {}
    for _label, field, _required in CSV_FIELDS[entity]:
        mapping[field] = next(
            (normalized[name] for name in aliases.get(field, ()) if name in normalized), ""
        )
    return mapping


def mapped_csv_preview(rows, entity, mapping):
    """Return mapped preview rows after validating required and unique mappings."""
    selected = [header for header in mapping.values() if header]
    if len(selected) != len(set(selected)):
        raise ValueError("A CSV column may be mapped to only one destination field.")
    missing = [label for label, field, required in CSV_FIELDS[entity] if required and not mapping.get(field)]
    if missing:
        raise ValueError("Map the required field(s): {}.".format(", ".join(missing)))
    return [
        {field: row.get(mapping.get(field), "") if mapping.get(field) else ""
         for _label, field, _required in CSV_FIELDS[entity]}
        for row in rows
    ]


class DataManagementRepository:
    """Read approved membership fields for duplicate review."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def _all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def duplicate_candidates(self):
        """Return deterministic possible person and family duplicate pairs."""
        people = self._all(
            "SELECT p.ID,TRIM(CONCAT_WS(' ',NULLIF(p.FirstName,''),"
            "NULLIF(p.MiddleName,''),NULLIF(p.LastName,''))),p.ChurchID "
            "FROM tblPerson p ORDER BY p.ChurchID,p.LastName,p.FirstName,p.ID"
        )
        families = self._all(
            "SELECT f.ID,COALESCE(f.FamilyName,''),f.ChurchID FROM tblFamily f "
            "ORDER BY f.ChurchID,f.FamilyName,f.ID"
        )
        contacts = self._all(
            "SELECT pc.PersonID,COALESCE(pc.Type,''),COALESCE(pc.Contact,''),"
            "TRIM(CONCAT_WS(' ',NULLIF(p.FirstName,''),NULLIF(p.MiddleName,''),"
            "NULLIF(p.LastName,''))),p.ChurchID FROM tblPersonContact pc "
            "JOIN tblPerson p ON p.ID=pc.PersonID WHERE COALESCE(pc.Contact,'')<>''"
        )
        addresses = self._all(
            "SELECT fa.FamilyID,TRIM(CONCAT_WS(' ',NULLIF(fa.Address,''),"
            "NULLIF(fa.Address2,''),NULLIF(fa.City,''),NULLIF(fa.State,''),"
            "NULLIF(fa.Zip,''))),COALESCE(f.FamilyName,''),f.ChurchID "
            "FROM tblFamilyAddress fa JOIN tblFamily f ON f.ID=fa.FamilyID "
            "WHERE COALESCE(fa.Address,'')<>''"
        )
        candidates = duplicate_pairs(
            people,
            lambda row: (row[2], normalized_text(row[1])),
            "Person", "Same full name",
        )
        candidates.extend(duplicate_pairs(
            [(row[0], row[3], row[4], row[1], row[2]) for row in contacts],
            lambda row: (row[2], normalized_contact(row[4])),
            "Person", "Same {}".format("contact information"),
        ))
        candidates.extend(duplicate_pairs(
            families,
            lambda row: (row[2], normalized_text(row[1])),
            "Family", "Same family name",
        ))
        candidates.extend(duplicate_pairs(
            [(row[0], row[2], row[3], row[1]) for row in addresses],
            lambda row: (row[2], normalized_text(row[3])),
            "Family", "Same mailing address",
        ))
        unique = {(item.entity, item.first_id, item.second_id, item.reason): item for item in candidates}
        return sorted(unique.values(), key=lambda item: (
            item.entity, item.first_name.casefold(), item.second_name.casefold(), item.reason,
        ))


class DataManagementDialog(wx.Dialog):
    """Central read-only duplicate review screen; imports follow in later phases."""

    def __init__(self, parent, connection):
        super().__init__(parent, title="Data Management", size=(980, 620))
        self.repository = DataManagementRepository(connection)
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label="Duplicate Review")
        title.SetFont(title.GetFont().Bold())
        outer.Add(title, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)
        outer.Add(wx.StaticText(
            panel,
            label="Possible matches are shown for review only. No records are changed.",
        ), 0, wx.ALL, 12)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Type", 85), ("First record", 245), ("ID", 65),
            ("Second record", 245), ("ID", 65), ("Reason", 210),
        )):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.status = wx.StaticText(panel, label="")
        outer.Add(self.status, 0, wx.ALL, 12)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        refresh = wx.Button(panel, label="Refresh Review")
        preview_csv = wx.Button(panel, label="Preview Membership CSV...")
        close = wx.Button(panel, label="Close")
        refresh.Bind(wx.EVT_BUTTON, lambda _event: self.refresh())
        preview_csv.Bind(wx.EVT_BUTTON, self.on_preview_csv)
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK))
        buttons.Add(refresh, 0, wx.RIGHT, 8)
        buttons.Add(preview_csv, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer()
        buttons.Add(close, 0)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(outer)
        self.refresh()

    def refresh(self):
        """Reload possible matches without changing database state."""
        self.list.DeleteAllItems()
        try:
            rows = self.repository.duplicate_candidates()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Review Duplicates", wx.OK | wx.ICON_ERROR, self)
            return
        for candidate in rows:
            index = self.list.InsertItem(self.list.GetItemCount(), candidate.entity)
            values = (
                candidate.first_name, str(candidate.first_id), candidate.second_name,
                str(candidate.second_id), candidate.reason,
            )
            for column, value in enumerate(values, 1):
                self.list.SetItem(index, column, value)
        self.status.SetLabel(
            "{} possible duplicate pair(s).".format(len(rows)) if rows
            else "No likely duplicates were found by the current exact-match rules."
        )

    def on_preview_csv(self, _event):
        """Open the non-writing CSV mapping and preview workflow."""
        dialog = CsvImportPreviewDialog(self)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()


class CsvImportPreviewDialog(wx.Dialog):
    """Preview an explicitly mapped membership CSV without database writes."""

    def __init__(self, parent):
        super().__init__(parent, title="Preview Membership CSV", size=(960, 680))
        self.headers = []
        self.rows = []
        self.mapping_choices = {}
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        instruction = wx.StaticText(
            panel,
            label="Choose People or Families, map the CSV columns, then preview. Preview makes no database changes.",
        )
        instruction.SetForegroundColour(wx.Colour(0, 76, 153))
        outer.Add(instruction, 0, wx.ALL, 12)

        source = wx.FlexGridSizer(cols=3, hgap=8, vgap=8)
        source.Add(wx.StaticText(panel, label="Record type"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.entity = wx.Choice(panel, choices=list(CSV_FIELDS), size=(180, -1))
        self.entity.SetSelection(0)
        self.entity.Bind(wx.EVT_CHOICE, self.on_entity)
        source.Add(self.entity, 0)
        source.Add((1, 1))
        source.Add(wx.StaticText(panel, label="CSV file"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.path = wx.TextCtrl(panel, style=wx.TE_READONLY)
        source.Add(self.path, 1, wx.EXPAND)
        browse = wx.Button(panel, label="Browse...")
        browse.Bind(wx.EVT_BUTTON, self.on_browse)
        source.Add(browse, 0)
        source.AddGrowableCol(1, 1)
        outer.Add(source, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        mapping_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "CSV column mapping")
        self.mapping_panel = wx.Panel(mapping_box.GetStaticBox())
        mapping_box.Add(self.mapping_panel, 1, wx.EXPAND | wx.ALL, 8)
        outer.Add(mapping_box, 0, wx.EXPAND | wx.ALL, 12)

        preview = wx.StaticBoxSizer(wx.VERTICAL, panel, "Preview")
        self.list = wx.ListCtrl(preview.GetStaticBox(), style=wx.LC_REPORT)
        preview.Add(self.list, 1, wx.EXPAND | wx.ALL, 6)
        outer.Add(preview, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.status = wx.StaticText(panel, label="Choose a CSV file to begin.")
        outer.Add(self.status, 0, wx.ALL, 12)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        run = wx.Button(panel, label="Preview Mapped Rows")
        run.Bind(wx.EVT_BUTTON, self.on_preview)
        close = wx.Button(panel, label="Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK))
        buttons.Add(run, 0)
        buttons.AddStretchSpacer()
        buttons.Add(close, 0)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(outer)
        self.rebuild_mapping()

    @property
    def entity_name(self):
        """Return the selected membership record type."""
        return self.entity.GetStringSelection()

    def rebuild_mapping(self, suggestions=None):
        """Rebuild destination mappings for the selected record type."""
        self.mapping_panel.DestroyChildren()
        self.mapping_choices = {}
        grid = wx.FlexGridSizer(cols=2, hgap=12, vgap=6)
        choices = ["Not mapped"] + self.headers
        for label, field, required in CSV_FIELDS[self.entity_name]:
            grid.Add(wx.StaticText(
                self.mapping_panel, label=label + (" *" if required else "")
            ), 0, wx.ALIGN_CENTER_VERTICAL)
            choice = wx.Choice(self.mapping_panel, choices=choices, size=(270, -1))
            selected = (suggestions or {}).get(field, "")
            choice.SetSelection(choices.index(selected) if selected in choices else 0)
            self.mapping_choices[field] = choice
            grid.Add(choice, 0, wx.EXPAND)
        grid.AddGrowableCol(1, 1)
        self.mapping_panel.SetSizer(grid)
        self.mapping_panel.Layout()
        self.Layout()

    def on_entity(self, _event):
        """Reset mappings when the record type changes."""
        suggestions = suggested_csv_mapping(self.headers, self.entity_name) if self.headers else None
        self.rebuild_mapping(suggestions)
        self.list.DeleteAllItems()
        self.status.SetLabel("Review the mappings, then preview the CSV rows.")

    def on_browse(self, _event):
        """Read a chosen CSV and prepare conservative mapping suggestions."""
        dialog = wx.FileDialog(self, "Choose membership CSV", wildcard="CSV files (*.csv)|*.csv")
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path = dialog.GetPath()
        finally:
            dialog.Destroy()
        try:
            self.headers, self.rows = read_csv_rows(path)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Read CSV", wx.OK | wx.ICON_ERROR, self)
            return
        self.path.SetValue(path)
        self.rebuild_mapping(suggested_csv_mapping(self.headers, self.entity_name))
        self.status.SetLabel("{} source row(s). Review every mapping before preview.".format(len(self.rows)))

    def on_preview(self, _event):
        """Render mapped rows without opening a database transaction."""
        if not self.rows:
            wx.MessageBox("Choose a CSV file first.", "Preview Membership CSV", wx.OK | wx.ICON_INFORMATION, self)
            return
        mapping = {
            field: (choice.GetStringSelection() if choice.GetSelection() > 0 else "")
            for field, choice in self.mapping_choices.items()
        }
        try:
            rows = mapped_csv_preview(self.rows, self.entity_name, mapping)
        except ValueError as error:
            wx.MessageBox(str(error), "Mapping Needs Attention", wx.OK | wx.ICON_WARNING, self)
            return
        self.list.ClearAll()
        fields = [(label, field) for label, field, _required in CSV_FIELDS[self.entity_name]]
        for index, (label, _field) in enumerate(fields):
            self.list.InsertColumn(index, label, width=140)
        for row in rows:
            index = self.list.InsertItem(self.list.GetItemCount(), row[fields[0][1]])
            for column, (_label, field) in enumerate(fields[1:], 1):
                self.list.SetItem(index, column, row[field])
        self.status.SetLabel(
            "Previewed {} {} row(s). No database records were created or changed.".format(
                len(rows), self.entity_name.lower()
            )
        )


def show_data_management(parent, connection):
    """Open the central ChurchManager Data Management dialog."""
    dialog = DataManagementDialog(parent, connection)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
