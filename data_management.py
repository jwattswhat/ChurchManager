"""Safe duplicate review foundation for ChurchManager data management."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import csv
import hashlib
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
        ("Title", "Title", False),
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
        "Title": ("title", "prefix"), "FamilyName": ("family name", "familyname", "household"),
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
    """Read approved membership fields and retain explicit review decisions."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def _all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def duplicate_candidates(self, include_deferred=False):
        """Return unresolved possible duplicates, optionally including deferred pairs."""
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
        resolutions = self._all(
            "SELECT EntityType,FirstRecordID,SecondRecordID,MatchReason,Resolution "
            "FROM tblDuplicateReviewResolution"
        )
        hidden = {
            (row[0], int(row[1]), int(row[2]), row[3])
            for row in resolutions if row[4] == "NOT_DUPLICATE" or not include_deferred
        }
        return sorted((item for key, item in unique.items() if key not in hidden), key=lambda item: (
            item.entity, item.first_name.casefold(), item.second_name.casefold(), item.reason,
        ))

    def resolve_duplicate(self, candidate, resolution, user_id, note=""):
        """Persist a non-destructive human decision for one advisory match."""
        if resolution not in ("NOT_DUPLICATE", "DEFERRED"):
            raise ValueError("Unsupported duplicate resolution.")
        first_id, second_id = sorted((int(candidate.first_id), int(candidate.second_id)))
        church_table = "tblPerson" if candidate.entity == "Person" else "tblFamily"
        rows = self._all(
            "SELECT ID,ChurchID FROM {} WHERE ID IN (?,?) ORDER BY ID".format(church_table),
            (first_id, second_id),
        )
        if len(rows) != 2 or int(rows[0][1]) != int(rows[1][1]):
            raise ValueError("Both records must still exist in the same church.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO tblDuplicateReviewResolution "
                "(ChurchID,EntityType,FirstRecordID,SecondRecordID,MatchReason,Resolution,"
                "ResolutionNote,ResolvedByUserID) VALUES (?,?,?,?,?,?,?,?) "
                "ON DUPLICATE KEY UPDATE Resolution=VALUES(Resolution),"
                "ResolutionNote=VALUES(ResolutionNote),ResolvedByUserID=VALUES(ResolvedByUserID),"
                "ResolvedAt=CURRENT_TIMESTAMP",
                (rows[0][1], candidate.entity, first_id, second_id, candidate.reason,
                 resolution, str(note or "").strip() or None, int(user_id)),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def churches(self):
        """Return positive-ID churches available as import destinations."""
        return self._all("SELECT ID,Church FROM tblChurch WHERE ID>0 ORDER BY Church,ID")


class MembershipImportService:
    """Validate and atomically import reviewed membership preview rows."""

    def __init__(self, connection, user_id):
        self.connection = portable_connection(connection)
        self.user_id = int(user_id)

    def _existing_keys(self, entity, church_id):
        cursor = self.connection.cursor()
        try:
            if entity == "People":
                cursor.execute(
                    "SELECT FirstName,LastName FROM tblPerson WHERE ChurchID=?", (church_id,)
                )
                names = {(normalized_text(row[0]), normalized_text(row[1])) for row in cursor.fetchall()}
                cursor.execute(
                    "SELECT pc.Contact FROM tblPersonContact pc JOIN tblPerson p ON p.ID=pc.PersonID "
                    "WHERE p.ChurchID=? AND COALESCE(pc.Contact,'')<>''", (church_id,)
                )
                contacts = {normalized_contact(row[0]) for row in cursor.fetchall()}
                return names, contacts
            cursor.execute("SELECT FamilyName FROM tblFamily WHERE ChurchID=?", (church_id,))
            names = {normalized_text(row[0]) for row in cursor.fetchall()}
            cursor.execute(
                "SELECT fc.Contact FROM tblFamilyContact fc JOIN tblFamily f ON f.ID=fc.FamilyID "
                "WHERE f.ChurchID=? AND COALESCE(fc.Contact,'')<>''", (church_id,)
            )
            contacts = {normalized_contact(row[0]) for row in cursor.fetchall()}
            return names, contacts
        finally:
            cursor.close()

    def validate(self, entity, church_id, rows):
        """Return row-numbered blocking errors without modifying the database."""
        if int(church_id) <= 0:
            return ["Select a valid church."]
        existing_names, existing_contacts = self._existing_keys(entity, int(church_id))
        seen_names, seen_contacts, errors = set(), set(), []
        for number, row in enumerate(rows, 2):
            for _label, field, _required in CSV_FIELDS[entity]:
                if len(str(row.get(field) or "")) > 255:
                    errors.append("Row {}: {} exceeds 255 characters.".format(number, field))
            if entity == "People":
                name = (normalized_text(row.get("FirstName")), normalized_text(row.get("LastName")))
            else:
                name = normalized_text(row.get("FamilyName"))
            if name in existing_names:
                errors.append("Row {}: the name already exists in the selected church.".format(number))
            if name in seen_names:
                errors.append("Row {}: the name is duplicated within this CSV.".format(number))
            seen_names.add(name)
            for field in ("Email", "Phone"):
                contact = normalized_contact(row.get(field))
                if contact and contact in existing_contacts:
                    errors.append("Row {}: {} already belongs to a record in this church.".format(number, field))
                if contact and contact in seen_contacts:
                    errors.append("Row {}: {} is duplicated within this CSV.".format(number, field))
                if contact:
                    seen_contacts.add(contact)
        return errors

    def import_rows(self, entity, church_id, rows, source_path):
        """Import fully reviewed rows in one transaction and record safe history."""
        errors = self.validate(entity, church_id, rows)
        if errors:
            raise ValueError("\n".join(errors[:12]))
        cursor = self.connection.cursor()
        try:
            for row in rows:
                if entity == "People":
                    cursor.execute(
                        "INSERT INTO tblPerson "
                        "(ChurchID,FirstName,MiddleName,LastName,Title,Status) VALUES (?,?,?,?,?,'Active')",
                        (church_id, row["FirstName"], row["MiddleName"] or None,
                         row["LastName"], row["Title"] or None),
                    )
                    record_id = cursor.lastrowid
                    self._insert_contacts(cursor, "Person", record_id, row)
                else:
                    cursor.execute(
                        "INSERT INTO tblFamily (ChurchID,FamilyName,Directory) VALUES (?,?,0)",
                        (church_id, row["FamilyName"]),
                    )
                    record_id = cursor.lastrowid
                    if any(row[field] for field in ("Address", "Address2", "City", "State", "Zip")):
                        cursor.execute(
                            "INSERT INTO tblFamilyAddress "
                            "(FamilyID,AddressLabel,Address,Address2,City,State,Zip,Unlisted) "
                            "VALUES (?,'Main',?,?,?,?,?,0)",
                            (record_id, row["Address"] or None, row["Address2"] or None,
                             row["City"] or None, row["State"] or None, row["Zip"] or None),
                        )
                    self._insert_contacts(cursor, "Family", record_id, row)
            source = Path(source_path)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            cursor.execute(
                "INSERT INTO tblMembershipImportHistory "
                "(ChurchID,ImportedByUserID,EntityType,SourceFileName,SourceSHA256,"
                "RowCount,ImportedCount,RejectedCount) VALUES (?,?,?,?,?,?,?,0)",
                (church_id, self.user_id, entity, source.name, digest, len(rows), len(rows)),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
        return len(rows)

    @staticmethod
    def _insert_contacts(cursor, entity, record_id, row):
        """Insert optional email and phone records using established contact tables."""
        parent = entity + "ID"
        table = "tbl{}Contact".format(entity)
        for kind in ("Email", "Phone"):
            value = row.get(kind)
            if value:
                cursor.execute(
                    "INSERT INTO {} ({},ContactLabel,Type,Contact,Unlisted) "
                    "VALUES (?,'Primary',?,?,0)".format(table, parent),
                    (record_id, kind, value),
                )


class MembershipExportService:
    """Create privacy-safe membership CSV exports and retain safe history."""

    def __init__(self, connection, user_id):
        self.connection = portable_connection(connection)
        self.user_id = int(user_id)

    def rows(self, entity, church_id):
        """Return approved export fields with every unlisted contact excluded."""
        cursor = self.connection.cursor()
        try:
            if entity == "People":
                cursor.execute(
                    "SELECT p.FirstName,COALESCE(p.MiddleName,''),p.LastName,COALESCE(p.Title,''),"
                    "COALESCE((SELECT pc.Contact FROM tblPersonContact pc "
                    "WHERE pc.PersonID=p.ID AND COALESCE(pc.Unlisted,0)=0 "
                    "AND LOWER(pc.Type)='email' ORDER BY pc.ID LIMIT 1),''),"
                    "COALESCE((SELECT pc.Contact FROM tblPersonContact pc "
                    "WHERE pc.PersonID=p.ID AND COALESCE(pc.Unlisted,0)=0 "
                    "AND LOWER(pc.Type)='phone' ORDER BY pc.ID LIMIT 1),'') "
                    "FROM tblPerson p WHERE p.ChurchID=? ORDER BY p.LastName,p.FirstName,p.ID",
                    (church_id,),
                )
                headers = ["First Name", "Middle Name", "Last Name", "Title", "Email", "Phone"]
            else:
                cursor.execute(
                    "SELECT f.FamilyName,COALESCE(fa.Address,''),COALESCE(fa.Address2,''),"
                    "COALESCE(fa.City,''),COALESCE(fa.State,''),COALESCE(fa.Zip,''),"
                    "COALESCE((SELECT fc.Contact FROM tblFamilyContact fc "
                    "WHERE fc.FamilyID=f.ID AND COALESCE(fc.Unlisted,0)=0 "
                    "AND LOWER(fc.Type)='email' ORDER BY fc.ID LIMIT 1),''),"
                    "COALESCE((SELECT fc.Contact FROM tblFamilyContact fc "
                    "WHERE fc.FamilyID=f.ID AND COALESCE(fc.Unlisted,0)=0 "
                    "AND LOWER(fc.Type)='phone' ORDER BY fc.ID LIMIT 1),'') "
                    "FROM tblFamily f LEFT JOIN tblFamilyAddress fa ON fa.ID=("
                    "SELECT MIN(candidate.ID) FROM tblFamilyAddress candidate "
                    "WHERE candidate.FamilyID=f.ID AND COALESCE(candidate.Unlisted,0)=0) "
                    "WHERE f.ChurchID=? ORDER BY f.FamilyName,f.ID",
                    (church_id,),
                )
                headers = [
                    "Family Name", "Address", "Address 2", "City", "State", "ZIP", "Email", "Phone",
                ]
            return headers, cursor.fetchall()
        finally:
            cursor.close()

    def export(self, entity, church_id, destination):
        """Write an approved CSV and record attribution without source content."""
        headers, rows = self.rows(entity, church_id)
        target = Path(destination)
        temporary = target.with_name(target.name + ".tmp")
        try:
            with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(headers)
                writer.writerows(rows)
            digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
            temporary.replace(target)
            cursor = self.connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO tblMembershipExportHistory "
                    "(ChurchID,ExportedByUserID,EntityType,DestinationFileName,ExportSHA256,"
                    "RowCount,IncludedUnlistedContacts) VALUES (?,?,?,?,?,?,0)",
                    (church_id, self.user_id, entity, target.name, digest, len(rows)),
                )
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                target.unlink(missing_ok=True)
                raise
            finally:
                cursor.close()
        finally:
            temporary.unlink(missing_ok=True)
        return len(rows)


class DataManagementDialog(wx.Dialog):
    """Central guarded duplicate review, membership import, and export screen."""

    def __init__(self, parent, connection, session):
        super().__init__(parent, title="Data Management", size=(980, 620))
        self.repository = DataManagementRepository(connection)
        self.connection = connection
        self.session = session
        self.rows = []
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label="Duplicate Review")
        title.SetFont(title.GetFont().Bold())
        outer.Add(title, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)
        outer.Add(wx.StaticText(
            panel,
            label=("Possible matches require human review. Decisions never delete, merge, "
                   "or alter membership records."),
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
        self.show_deferred = wx.CheckBox(panel, label="Include matches marked Review Later")
        self.show_deferred.Bind(wx.EVT_CHECKBOX, lambda _event: self.refresh())
        outer.Add(self.show_deferred, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        refresh = wx.Button(panel, label="Refresh Review")
        not_duplicate = wx.Button(panel, label="Not Duplicates")
        defer = wx.Button(panel, label="Review Later")
        preview_csv = wx.Button(panel, label="Preview Membership CSV...")
        export_csv = wx.Button(panel, label="Export Membership CSV...")
        close = wx.Button(panel, label="Close")
        refresh.Bind(wx.EVT_BUTTON, lambda _event: self.refresh())
        not_duplicate.Bind(wx.EVT_BUTTON, self.on_not_duplicate)
        defer.Bind(wx.EVT_BUTTON, self.on_defer)
        preview_csv.Bind(wx.EVT_BUTTON, self.on_preview_csv)
        export_csv.Bind(wx.EVT_BUTTON, self.on_export_csv)
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK))
        buttons.Add(refresh, 0, wx.RIGHT, 8)
        buttons.Add(not_duplicate, 0, wx.RIGHT, 8)
        buttons.Add(defer, 0, wx.RIGHT, 8)
        buttons.Add(preview_csv, 0, wx.RIGHT, 8)
        buttons.Add(export_csv, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer()
        buttons.Add(close, 0)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(outer)
        self.refresh()

    def refresh(self):
        """Reload possible matches without changing database state."""
        self.list.DeleteAllItems()
        try:
            rows = self.repository.duplicate_candidates(self.show_deferred.GetValue())
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Review Duplicates", wx.OK | wx.ICON_ERROR, self)
            return
        self.rows = rows
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

    def _selected_candidate(self):
        """Return the selected advisory match or explain that selection is required."""
        selected = self.list.GetFirstSelected()
        if selected < 0 or selected >= len(self.rows):
            wx.MessageBox("Select a possible duplicate pair first.", "Duplicate Review",
                          wx.OK | wx.ICON_INFORMATION, self)
            return None
        return self.rows[selected]

    def _resolve(self, resolution, prompt):
        """Confirm and store a non-destructive duplicate-review decision."""
        candidate = self._selected_candidate()
        if candidate is None:
            return
        message = "{}\n\n{} (ID {})\n{} (ID {})".format(
            prompt, candidate.first_name, candidate.first_id,
            candidate.second_name, candidate.second_id,
        )
        if wx.MessageBox(message, "Confirm Duplicate Review", wx.YES_NO | wx.NO_DEFAULT |
                         wx.ICON_QUESTION, self) != wx.YES:
            return
        try:
            self.repository.resolve_duplicate(candidate, resolution, self.session.user_id)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Save Review", wx.OK | wx.ICON_ERROR, self)
            return
        self.refresh()

    def on_not_duplicate(self, _event):
        """Record that the selected records are distinct without changing either one."""
        self._resolve("NOT_DUPLICATE", "Mark these as separate records, not duplicates?")

    def on_defer(self, _event):
        """Remove the selected match from the active queue for later review."""
        self._resolve("DEFERRED", "Defer this possible match for later review?")

    def on_preview_csv(self, _event):
        """Open the non-writing CSV mapping and preview workflow."""
        dialog = CsvImportPreviewDialog(self, self.connection, self.session)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

    def on_export_csv(self, _event):
        """Open the privacy-safe membership export workflow."""
        dialog = MembershipExportDialog(self, self.connection, self.session)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()


class MembershipExportDialog(wx.Dialog):
    """Collect a bounded membership export destination and show its privacy rule."""

    def __init__(self, parent, connection, session):
        super().__init__(parent, title="Export Membership CSV", size=(600, 310))
        self.service = MembershipExportService(connection, session.user_id)
        self.church_rows = DataManagementRepository(connection).churches()
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        notice = wx.StaticText(
            panel,
            label=("Exports contain only membership directory fields. Unlisted addresses, email "
                   "addresses, and telephone numbers are always omitted."),
        )
        notice.Wrap(550)
        notice.SetForegroundColour(wx.Colour(0, 76, 153))
        outer.Add(notice, 0, wx.ALL, 14)
        grid = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        grid.Add(wx.StaticText(panel, label="Record type"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.entity = wx.Choice(panel, choices=list(CSV_FIELDS))
        self.entity.SetSelection(0)
        grid.Add(self.entity, 1, wx.EXPAND)
        grid.Add(wx.StaticText(panel, label="Church"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.church = wx.Choice(panel, choices=[row[1] for row in self.church_rows])
        if self.church_rows:
            self.church.SetSelection(0)
        grid.Add(self.church, 1, wx.EXPAND)
        grid.AddGrowableCol(1, 1)
        outer.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        outer.AddStretchSpacer()
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        export = wx.Button(panel, label="Choose File and Export...")
        export.Bind(wx.EVT_BUTTON, self.on_export)
        close = wx.Button(panel, label="Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK))
        buttons.Add(export, 0)
        buttons.AddStretchSpacer()
        buttons.Add(close, 0)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14)
        panel.SetSizer(outer)

    def on_export(self, _event):
        """Choose the target, confirm disclosure, and write the safe export."""
        if self.church.GetSelection() < 0:
            wx.MessageBox("Select a church.", "Export Membership CSV", wx.OK | wx.ICON_WARNING, self)
            return
        entity = self.entity.GetStringSelection()
        church_id, church_name = self.church_rows[self.church.GetSelection()]
        dialog = wx.FileDialog(
            self, "Save privacy-safe membership export",
            defaultFile="{}-{}.csv".format(church_name, entity).replace(" ", "-"),
            wildcard="CSV files (*.csv)|*.csv", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            destination = dialog.GetPath()
        finally:
            dialog.Destroy()
        confirmation = (
            "Export {} directory fields for {}?\n\n"
            "Unlisted contact information and confidential subsystems are excluded."
        ).format(entity.lower(), church_name)
        if wx.MessageBox(confirmation, "Confirm Membership Export", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES:
            return
        try:
            count = self.service.export(entity, church_id, destination)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Export Membership CSV", wx.OK | wx.ICON_ERROR, self)
            return
        wx.MessageBox(
            "Exported {} {} row(s).".format(count, entity.lower()),
            "Membership Export Complete", wx.OK | wx.ICON_INFORMATION, self,
        )


class CsvImportPreviewDialog(wx.Dialog):
    """Preview an explicitly mapped membership CSV without database writes."""

    def __init__(self, parent, connection, session):
        super().__init__(parent, title="Preview Membership CSV", size=(960, 680))
        self.headers = []
        self.rows = []
        self.mapping_choices = {}
        self.import_service = MembershipImportService(connection, session.user_id)
        self.church_rows = DataManagementRepository(connection).churches()
        self.preview_rows = []
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
        source.Add(wx.StaticText(panel, label="Church"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.church = wx.Choice(panel, choices=[row[1] for row in self.church_rows])
        if self.church_rows:
            self.church.SetSelection(0)
        self.church.Bind(wx.EVT_CHOICE, self.on_mapping_changed)
        source.Add(self.church, 1, wx.EXPAND)
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
        self.import_button = wx.Button(panel, label="Import Reviewed Rows")
        self.import_button.Disable()
        self.import_button.Bind(wx.EVT_BUTTON, self.on_import)
        close = wx.Button(panel, label="Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK))
        buttons.Add(run, 0)
        buttons.Add(self.import_button, 0, wx.LEFT, 8)
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
        grid = self.mapping_panel.GetSizer()
        if grid is None:
            grid = wx.FlexGridSizer(cols=2, hgap=12, vgap=6)
            grid.AddGrowableCol(1, 1)
            self.mapping_panel.SetSizer(grid)
        else:
            grid.Clear(delete_windows=True)
        self.mapping_choices = {}
        choices = ["Not mapped"] + self.headers
        for label, field, required in CSV_FIELDS[self.entity_name]:
            grid.Add(wx.StaticText(
                self.mapping_panel, label=label + (" *" if required else "")
            ), 0, wx.ALIGN_CENTER_VERTICAL)
            choice = wx.Choice(self.mapping_panel, choices=choices, size=(270, -1))
            selected = (suggestions or {}).get(field, "")
            choice.SetSelection(choices.index(selected) if selected in choices else 0)
            self.mapping_choices[field] = choice
            choice.Bind(wx.EVT_CHOICE, self.on_mapping_changed)
            grid.Add(choice, 0, wx.EXPAND)
        self.mapping_panel.Layout()
        self.Layout()

    def on_mapping_changed(self, _event):
        """Require a fresh preview after any destination or mapping change."""
        self.preview_rows = []
        self.import_button.Disable()
        self.status.SetLabel("Mapping or destination changed. Preview the rows again before import.")

    def on_entity(self, _event):
        """Reset mappings when the record type changes."""
        suggestions = suggested_csv_mapping(self.headers, self.entity_name) if self.headers else None
        self.rebuild_mapping(suggestions)
        self.list.DeleteAllItems()
        self.preview_rows = []
        self.import_button.Disable()
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
        self.preview_rows = []
        self.import_button.Disable()
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
        if self.church.GetSelection() < 0:
            wx.MessageBox("Select a church.", "Mapping Needs Attention", wx.OK | wx.ICON_WARNING, self)
            return
        errors = self.import_service.validate(
            self.entity_name, self.church_rows[self.church.GetSelection()][0], rows
        )
        self.list.ClearAll()
        fields = [(label, field) for label, field, _required in CSV_FIELDS[self.entity_name]]
        for index, (label, _field) in enumerate(fields):
            self.list.InsertColumn(index, label, width=140)
        for row in rows:
            index = self.list.InsertItem(self.list.GetItemCount(), row[fields[0][1]])
            for column, (_label, field) in enumerate(fields[1:], 1):
                self.list.SetItem(index, column, row[field])
        self.status.SetLabel(
            ("Preview needs attention: " + errors[0]) if errors else
            "Previewed {} {} row(s). No database records were created or changed.".format(
                len(rows), self.entity_name.lower())
        )
        self.preview_rows = rows if not errors else []
        self.import_button.Enable(not errors)

    def on_import(self, _event):
        """Require explicit confirmation before the atomic reviewed import."""
        if not self.preview_rows or self.church.GetSelection() < 0:
            return
        church_id, church_name = self.church_rows[self.church.GetSelection()]
        message = (
            "Import {} reviewed {} row(s) into {}?\n\n"
            "This creates new records. It does not merge or replace existing records."
        ).format(len(self.preview_rows), self.entity_name.lower(), church_name)
        if wx.MessageBox(message, "Confirm Membership Import", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES:
            return
        try:
            count = self.import_service.import_rows(
                self.entity_name, church_id, self.preview_rows, self.path.GetValue()
            )
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Import Membership CSV", wx.OK | wx.ICON_ERROR, self)
            return
        wx.MessageBox(
            "Imported {} new {} record(s).".format(count, self.entity_name.lower()),
            "Membership Import Complete", wx.OK | wx.ICON_INFORMATION, self,
        )
        self.preview_rows = []
        self.import_button.Disable()
        self.status.SetLabel("Import complete. Choose another file or close this window.")


def show_data_management(parent, connection, session):
    """Open the central ChurchManager Data Management dialog."""
    dialog = DataManagementDialog(parent, connection, session)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
