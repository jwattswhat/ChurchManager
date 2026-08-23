"""Safe duplicate review foundation for ChurchManager data management."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
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
        close = wx.Button(panel, label="Close")
        refresh.Bind(wx.EVT_BUTTON, lambda _event: self.refresh())
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK))
        buttons.Add(refresh, 0, wx.RIGHT, 8)
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


def show_data_management(parent, connection):
    """Open the central ChurchManager Data Management dialog."""
    dialog = DataManagementDialog(parent, connection)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
