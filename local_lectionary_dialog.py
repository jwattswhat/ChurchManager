"""Manage congregation-created lectionary systems and editions."""

from __future__ import annotations

from uuid import uuid4

import wx

from bulletin_orders import portable_connection
from lectionary_calendar import LectionaryCalendarError, rule_date
def local_key(kind):
    """Return an immutable key in ChurchManager's reserved local namespace."""
    return f"local-{kind}-{uuid4().hex}"


def clean_name(value, label="Name"):
    """Return a bounded required display name."""
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{label} is required.")
    if len(value) > 255:
        raise ValueError(f"{label} is too long.")
    return value


def dialog_buttons(panel):
    """Create standard buttons whose parent matches the panel's sizer."""
    buttons = wx.StdDialogButtonSizer()
    buttons.AddButton(wx.Button(panel, wx.ID_OK))
    buttons.AddButton(wx.Button(panel, wx.ID_CANCEL))
    buttons.Realize()
    return buttons


class LocalLectionaryRepository:
    """Persist only unowned local systems and editions."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    @staticmethod
    def _require_record(cursor, sql, values, message):
        """Confirm a protected local record exists before allowing an update.

        MariaDB reports zero affected rows when an UPDATE writes the values that
        are already stored.  Existence must therefore be checked separately from
        ``rowcount`` so an unchanged record remains a valid save.
        """
        cursor.execute(sql, values)
        if not cursor.fetchone():
            raise ValueError(message)

    def systems(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,Name,CycleType,Active,Note FROM tblLectionarySystem "
                "WHERE PackageID IS NULL ORDER BY Active DESC,Name"
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def editions(self, system_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,Name,EditionYear,CycleRule,IsActive,SourceNote "
                "FROM tblLectionaryEdition WHERE LectionarySystemID=? "
                "AND PackageID IS NULL ORDER BY IsActive DESC,Name", (system_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def cycles(self, edition_id):
        """Return cycles belonging to one local edition."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT c.ID,c.DisplayName,c.Sequence,c.IsActive,c.CycleCode "
                "FROM tblLectionaryCycle c JOIN tblLectionaryEdition e "
                "ON e.ID=c.LectionaryEditionID WHERE c.LectionaryEditionID=? "
                "AND e.PackageID IS NULL ORDER BY c.IsActive DESC,c.Sequence,c.DisplayName",
                (edition_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def propers(self, edition_id):
        """Return active and retired Propers belonging to one local edition."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT p.ID,p.LiturgicalDate,p.Season,p.Sort,p.Color,p.AltColor,"
                "p.CalendarRule,p.IsActive,p.Note,p.LectionaryCycleID,"
                "COALESCE(c.DisplayName,'No cycle') FROM tblPropers p "
                "JOIN tblLectionaryEdition e ON e.ID=p.LectionaryEditionID "
                "LEFT JOIN tblLectionaryCycle c ON c.ID=p.LectionaryCycleID "
                "WHERE p.LectionaryEditionID=? AND p.PackageID IS NULL "
                "AND e.PackageID IS NULL ORDER BY p.IsActive DESC,p.Sort,p.LiturgicalDate",
                (edition_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def save_system(self, record_id, name, cycle_type, note):
        """Create or update one local system without touching package data."""
        name = clean_name(name, "System name")
        if cycle_type not in {"None", "ABC", "Custom"}:
            raise ValueError("Cycle type must be None, ABC, or Custom.")
        cursor = self.connection.cursor()
        try:
            if record_id is None:
                cursor.execute(
                    "INSERT INTO tblLectionarySystem "
                    "(SystemCode,Name,CycleType,Active,Note,PackageID,IsStarter) "
                    "VALUES (?,?,?,1,?,NULL,0)",
                    (local_key("system"), name, cycle_type, str(note or "").strip() or None),
                )
                record_id = cursor.lastrowid
            else:
                self._require_record(
                    cursor,
                    "SELECT ID FROM tblLectionarySystem WHERE ID=? AND PackageID IS NULL",
                    (record_id,), "The local lectionary system is unavailable.",
                )
                cursor.execute(
                    "UPDATE tblLectionarySystem SET Name=?,CycleType=?,Note=? "
                    "WHERE ID=? AND PackageID IS NULL",
                    (name, cycle_type, str(note or "").strip() or None, record_id),
                )
            self.connection.commit()
            return record_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save_edition(self, record_id, system_id, name, year, cycle_rule, source_note):
        """Create or update an edition owned by a local system."""
        name = clean_name(name, "Edition name")
        year = str(year or "").strip()
        if year:
            try:
                year = int(year)
            except ValueError as error:
                raise ValueError("Edition year must be a four-digit year or blank.") from error
            if year < 1000 or year > 9999:
                raise ValueError("Edition year must be a four-digit year or blank.")
        else:
            year = None
        cycle_rule = str(cycle_rule or "none").strip().casefold() or "none"
        if cycle_rule not in {"none", "advent-year-abc"}:
            raise ValueError("Cycle rotation must be none or Advent-year A/B/C.")
        source_note = str(source_note or "").strip()
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,CycleType FROM tblLectionarySystem WHERE ID=? AND PackageID IS NULL "
                "AND Active=1", (system_id,),
            )
            system = cursor.fetchone()
            if not system:
                raise ValueError("Select an active local lectionary system.")
            if cycle_rule == "advent-year-abc" and system[1] != "ABC":
                raise ValueError("Advent-year A/B/C rotation requires an A/B/C system.")
            values = (system_id, name, year, source_note or None, cycle_rule)
            if record_id is None:
                cursor.execute(
                    "INSERT INTO tblLectionaryEdition "
                    "(LectionarySystemID,EditionCode,Name,EditionYear,Status,PackageID,"
                    "IsStarter,IsActive,SourceNote,ResolverVersion,CycleRule) "
                    "VALUES (?,?,?,?,'LOCAL',NULL,0,1,?,'1',?)",
                    (system_id, local_key("edition"), name, year,
                     source_note or None, cycle_rule),
                )
                record_id = cursor.lastrowid
            else:
                self._require_record(
                    cursor,
                    "SELECT ID FROM tblLectionaryEdition WHERE ID=? AND PackageID IS NULL",
                    (record_id,), "The local lectionary edition is unavailable.",
                )
                cursor.execute(
                    "UPDATE tblLectionaryEdition SET LectionarySystemID=?,Name=?,"
                    "EditionYear=?,SourceNote=?,CycleRule=? WHERE ID=? AND PackageID IS NULL",
                    values + (record_id,),
                )
            if system[1] == "ABC":
                for code, display, sequence in (
                    ("a", "Year A", 1), ("b", "Year B", 2), ("c", "Year C", 3),
                ):
                    cursor.execute(
                        "INSERT INTO tblLectionaryCycle "
                        "(LectionaryEditionID,CycleCode,DisplayName,Sequence,IsActive) "
                        "VALUES (?,?,?,?,1) ON DUPLICATE KEY UPDATE "
                        "DisplayName=VALUES(DisplayName),Sequence=VALUES(Sequence),IsActive=1",
                        (record_id, code, display, sequence),
                    )
            self.connection.commit()
            return record_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def set_active(self, table, record_id, active):
        """Activate or retire a local system or edition."""
        if table not in {"tblLectionarySystem", "tblLectionaryEdition"}:
            raise ValueError("Unsupported local lectionary record type.")
        active_column = "Active" if table == "tblLectionarySystem" else "IsActive"
        cursor = self.connection.cursor()
        try:
            self._require_record(
                cursor, f"SELECT ID FROM {table} WHERE ID=? AND PackageID IS NULL",
                (record_id,), "The local lectionary record is unavailable.",
            )
            cursor.execute(
                f"UPDATE {table} SET {active_column}=? WHERE ID=? AND PackageID IS NULL",
                (int(bool(active)), record_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save_cycle(self, record_id, edition_id, display_name, sequence):
        """Create or update a cycle under a congregation-owned edition."""
        display_name = clean_name(display_name, "Cycle name")
        try:
            sequence = int(str(sequence).strip())
        except ValueError as error:
            raise ValueError("Cycle sequence must be a positive whole number.") from error
        if sequence < 1:
            raise ValueError("Cycle sequence must be a positive whole number.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID FROM tblLectionaryEdition WHERE ID=? AND PackageID IS NULL "
                "AND IsActive=1", (edition_id,),
            )
            if not cursor.fetchone():
                raise ValueError("Select an active local edition.")
            if record_id is None:
                cursor.execute(
                    "INSERT INTO tblLectionaryCycle "
                    "(LectionaryEditionID,CycleCode,DisplayName,Sequence,IsActive) "
                    "VALUES (?,?,?,?,1)",
                    (edition_id, local_key("cycle"), display_name, sequence),
                )
                record_id = cursor.lastrowid
            else:
                self._require_record(
                    cursor,
                    "SELECT c.ID FROM tblLectionaryCycle c JOIN tblLectionaryEdition e "
                    "ON e.ID=c.LectionaryEditionID WHERE c.ID=? "
                    "AND c.LectionaryEditionID=? AND e.PackageID IS NULL",
                    (record_id, edition_id),
                    "The local lectionary cycle is unavailable.",
                )
                cursor.execute(
                    "UPDATE tblLectionaryCycle c JOIN tblLectionaryEdition e "
                    "ON e.ID=c.LectionaryEditionID SET c.DisplayName=?,c.Sequence=? "
                    "WHERE c.ID=? AND c.LectionaryEditionID=? AND e.PackageID IS NULL",
                    (display_name, sequence, record_id, edition_id),
                )
            self.connection.commit()
            return record_id
        except Exception as error:
            self.connection.rollback()
            if "duplicate" in str(error).casefold():
                raise ValueError("That cycle sequence is already used in this edition.") from error
            raise
        finally:
            cursor.close()

    def set_cycle_active(self, cycle_id, edition_id, active):
        """Retire or restore a cycle only when its edition is local."""
        cursor = self.connection.cursor()
        try:
            self._require_record(
                cursor,
                "SELECT c.ID FROM tblLectionaryCycle c JOIN tblLectionaryEdition e "
                "ON e.ID=c.LectionaryEditionID WHERE c.ID=? "
                "AND c.LectionaryEditionID=? AND e.PackageID IS NULL",
                (cycle_id, edition_id), "The local lectionary cycle is unavailable.",
            )
            cursor.execute(
                "UPDATE tblLectionaryCycle c JOIN tblLectionaryEdition e "
                "ON e.ID=c.LectionaryEditionID SET c.IsActive=? "
                "WHERE c.ID=? AND c.LectionaryEditionID=? AND e.PackageID IS NULL",
                (int(bool(active)), cycle_id, edition_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save_proper(self, record_id, edition_id, cycle_id, liturgical_date,
                    season, sort, color, alternate_color, calendar_rule, note):
        """Create or update a citation-only Proper under a local edition."""
        liturgical_date = clean_name(liturgical_date, "Liturgical date")
        try:
            sort = int(str(sort).strip())
        except ValueError as error:
            raise ValueError("Sort must be a whole number.") from error
        calendar_rule = str(calendar_rule or "").strip().casefold()
        if calendar_rule:
            try:
                rule_date(calendar_rule, 2026)
            except LectionaryCalendarError as error:
                raise ValueError(str(error)) from error
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT LectionarySystemID FROM tblLectionaryEdition "
                "WHERE ID=? AND PackageID IS NULL AND IsActive=1", (edition_id,),
            )
            edition = cursor.fetchone()
            if not edition:
                raise ValueError("Select an active local edition.")
            if cycle_id is not None:
                cursor.execute(
                    "SELECT ID,CycleCode FROM tblLectionaryCycle WHERE ID=? "
                    "AND LectionaryEditionID=? AND IsActive=1", (cycle_id, edition_id),
                )
                cycle = cursor.fetchone()
                if not cycle:
                    raise ValueError("Select an active cycle from this edition.")
                cycle_label = str(cycle[1]).upper()
            else:
                cycle_label = None
            values = (
                edition[0], edition_id, cycle_id, cycle_label, sort,
                str(season or "").strip() or None, liturgical_date,
                str(color or "").strip() or None,
                str(alternate_color or "").strip() or None,
                calendar_rule or None,
                str(note or "").strip() or None,
            )
            if record_id is None:
                cursor.execute(
                    "INSERT INTO tblPropers "
                    "(LectionarySystemID,LectionaryEditionID,LectionaryCycleID,ProperKey,"
                    "Cycle,Sort,Season,LiturgicalDate,Color,AltColor,CalendarRule,PackageID,"
                    "IsStarter,IsActive,Theme,Note,SourceNote) "
                    "VALUES (?,?,?, ?,?,?,?,?,?,?,?,NULL,0,1,'',?,NULL)",
                    values[:3] + (local_key("proper"),) + values[3:],
                )
                record_id = cursor.lastrowid
            else:
                self._require_record(
                    cursor,
                    "SELECT p.ID FROM tblPropers p JOIN tblLectionaryEdition e "
                    "ON e.ID=p.LectionaryEditionID WHERE p.ID=? "
                    "AND p.LectionaryEditionID=? AND p.PackageID IS NULL "
                    "AND e.PackageID IS NULL",
                    (record_id, edition_id), "The local Proper is unavailable.",
                )
                cursor.execute(
                    "UPDATE tblPropers SET LectionarySystemID=?,LectionaryEditionID=?,"
                    "LectionaryCycleID=?,Cycle=?,Sort=?,Season=?,LiturgicalDate=?,Color=?,"
                    "AltColor=?,CalendarRule=?,Note=? WHERE ID=? AND PackageID IS NULL",
                    values + (record_id,),
                )
            self.connection.commit()
            return record_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def set_proper_active(self, proper_id, edition_id, active):
        """Retire or restore a Proper only inside its local edition."""
        cursor = self.connection.cursor()
        try:
            self._require_record(
                cursor,
                "SELECT p.ID FROM tblPropers p JOIN tblLectionaryEdition e "
                "ON e.ID=p.LectionaryEditionID WHERE p.ID=? "
                "AND p.LectionaryEditionID=? AND p.PackageID IS NULL "
                "AND e.PackageID IS NULL",
                (proper_id, edition_id), "The local Proper is unavailable.",
            )
            cursor.execute(
                "UPDATE tblPropers p JOIN tblLectionaryEdition e "
                "ON e.ID=p.LectionaryEditionID SET p.IsActive=? "
                "WHERE p.ID=? AND p.LectionaryEditionID=? AND p.PackageID IS NULL "
                "AND e.PackageID IS NULL", (int(bool(active)), proper_id, edition_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()


class _SystemDialog(wx.Dialog):
    def __init__(self, parent, row=None):
        super().__init__(parent, title="Local Lectionary System", size=(500, 330))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(2, 8, 8); grid.AddGrowableCol(1, 1)
        self.name = wx.TextCtrl(panel, value=str(row[1] or "") if row else "")
        self.cycle = wx.Choice(panel, choices=["None", "ABC", "Custom"])
        self.cycle.SetStringSelection(str(row[2]) if row else "None")
        self.note = wx.TextCtrl(panel, value=str(row[4] or "") if row else "",
                                style=wx.TE_MULTILINE)
        for label, control in (("System name", self.name), ("Cycle type", self.cycle),
                               ("Note", self.note)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.ALL, 12)
        outer.Add(dialog_buttons(panel), 0,
                  wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer)


class _EditionDialog(wx.Dialog):
    def __init__(self, parent, row=None):
        super().__init__(parent, title="Local Lectionary Edition", size=(540, 360))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(2, 8, 8); grid.AddGrowableCol(1, 1)
        self.name = wx.TextCtrl(panel, value=str(row[1] or "") if row else "")
        self.year = wx.TextCtrl(panel, value=str(row[2] or "") if row else "")
        self.rule = wx.Choice(panel, choices=["none", "advent-year-abc"])
        self.rule.SetStringSelection(str(row[3] or "none") if row else "none")
        self.note = wx.TextCtrl(panel, value=str(row[5] or "") if row else "",
                                style=wx.TE_MULTILINE)
        for label, control in (("Edition name", self.name), ("Edition year", self.year),
                               ("Cycle rotation", self.rule), ("Source note", self.note)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.ALL, 12)
        outer.Add(dialog_buttons(panel), 0,
                  wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer)


class _CycleDialog(wx.Dialog):
    def __init__(self, parent, row=None):
        super().__init__(parent, title="Local Lectionary Cycle", size=(440, 210))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(2, 8, 8); grid.AddGrowableCol(1, 1)
        self.name = wx.TextCtrl(panel, value=str(row[1] or "") if row else "")
        self.sequence = wx.SpinCtrl(panel, min=1, max=9999,
                                    initial=int(row[2]) if row else 1)
        for label, control in (("Cycle name", self.name), ("Sequence", self.sequence)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.ALL, 12)
        outer.Add(dialog_buttons(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer)


class _ProperDialog(wx.Dialog):
    def __init__(self, parent, cycles, row=None):
        super().__init__(parent, title="Local Proper", size=(610, 540))
        self.cycles = [(None, "No cycle")] + [(item[0], item[1]) for item in cycles if item[3]]
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(2, 8, 8); grid.AddGrowableCol(1, 1)
        self.date = wx.TextCtrl(panel, value=str(row[1] or "") if row else "")
        self.season = wx.TextCtrl(panel, value=str(row[2] or "") if row else "")
        self.sort = wx.SpinCtrl(panel, min=0, max=999999, initial=int(row[3]) if row else 10)
        self.cycle = wx.Choice(panel, choices=[item[1] for item in self.cycles])
        cycle_id = row[9] if row else None
        self.cycle.SetSelection(next((i for i, item in enumerate(self.cycles) if item[0] == cycle_id), 0))
        self.color = wx.TextCtrl(panel, value=str(row[4] or "") if row else "")
        self.alt_color = wx.TextCtrl(panel, value=str(row[5] or "") if row else "")
        self.rule = wx.TextCtrl(panel, value=str(row[6] or "") if row else "")
        self.note = wx.TextCtrl(panel, value=str(row[8] or "") if row else "", style=wx.TE_MULTILINE)
        for label, control in (
            ("Liturgical date", self.date), ("Season", self.season), ("Cycle", self.cycle),
            ("Sort", self.sort), ("Liturgical color", self.color),
            ("Alternate color", self.alt_color), ("Calendar rule", self.rule),
            ("Note", self.note),
        ):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        help_text = wx.StaticText(panel, label=(
            "Calendar rules are optional. Examples: fixed:12-25, easter-offset:0, "
            "advent-sunday-1, first-sunday-after:07-04."
        ))
        help_text.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(grid, 1, wx.EXPAND | wx.ALL, 12)
        outer.Add(help_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        outer.Add(dialog_buttons(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer)

    def cycle_id(self):
        return self.cycles[self.cycle.GetSelection()][0]


class _PropersDialog(wx.Dialog):
    def __init__(self, parent, repository, edition):
        super().__init__(parent, title=f"Local Propers — {edition[1]}", size=(940, 600),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = repository; self.edition = edition; self.rows = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label=(
            "These Propers belong to this congregation. Double-click a row to edit it."
        ))
        note.SetForegroundColour(wx.Colour(0, 90, 190)); outer.Add(note, 0, wx.ALL, 10)
        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Liturgical date", 250), ("Season", 120), ("Cycle", 100),
                             ("Sort", 65), ("Color", 90), ("Calendar rule", 190),
                             ("Active", 65)):
            self.grid.AppendColumn(label, width=width)
        outer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("Add Proper", self.on_add), ("Edit Proper", self.on_edit),
                               ("Retire / Restore", self.on_toggle)):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler)
            actions.Add(button, 0, wx.RIGHT, 7)
        actions.AddStretchSpacer(); close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE)); actions.Add(close)
        outer.Add(actions, 0, wx.EXPAND | wx.ALL, 10); panel.SetSizer(outer)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit)
        self.refresh(); self.CentreOnParent()

    def refresh(self, selected_id=None):
        self.rows = self.repository.propers(self.edition[0]); self.grid.DeleteAllItems()
        for index, row in enumerate(self.rows):
            self.grid.InsertItem(index, str(row[1])); self.grid.SetItem(index, 1, str(row[2] or ""))
            self.grid.SetItem(index, 2, str(row[10])); self.grid.SetItem(index, 3, str(row[3]))
            self.grid.SetItem(index, 4, str(row[4] or "")); self.grid.SetItem(index, 5, str(row[6] or ""))
            self.grid.SetItem(index, 6, "Yes" if row[7] else "No")
            if row[0] == selected_id: self.grid.Select(index)

    def on_add(self, _event): self._edit(None)
    def on_edit(self, _event):
        index = self.grid.GetFirstSelected()
        if index >= 0: self._edit(self.rows[index])
    def _edit(self, row):
        cycles = self.repository.cycles(self.edition[0]); dialog = _ProperDialog(self, cycles, row)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            try:
                proper_id = self.repository.save_proper(
                    row[0] if row else None, self.edition[0], dialog.cycle_id(),
                    dialog.date.GetValue(), dialog.season.GetValue(), dialog.sort.GetValue(),
                    dialog.color.GetValue(), dialog.alt_color.GetValue(), dialog.rule.GetValue(),
                    dialog.note.GetValue(),
                )
                self.refresh(proper_id)
            except Exception as error:
                wx.MessageBox(str(error), "Local Proper", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()
    def on_toggle(self, _event):
        index = self.grid.GetFirstSelected()
        if index < 0: return
        row = self.rows[index]
        try:
            self.repository.set_proper_active(row[0], self.edition[0], not row[7]); self.refresh(row[0])
        except Exception as error:
            wx.MessageBox(str(error), "Local Proper", wx.OK | wx.ICON_ERROR, self)


class LocalLectionaryDialog(wx.Dialog):
    """Present the local system/edition hierarchy without package-owned rows."""

    def __init__(self, parent, connection, authorization):
        authorization.require("worship.manage", operation="Manage local lectionaries")
        super().__init__(parent, title="Local Lectionaries", size=(980, 600),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = LocalLectionaryRepository(connection)
        self.system_rows = []; self.edition_rows = []; self.cycle_rows = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label=(
            "Create congregation-owned lectionaries here. Installed package records are "
            "protected and are managed separately under Lectionary Packages."
        ))
        note.SetForegroundColour(wx.Colour(0, 90, 190)); outer.Add(note, 0, wx.ALL, 10)
        body = wx.BoxSizer(wx.HORIZONTAL)
        self.systems = self._list(panel, (("System", 250), ("Cycle", 90), ("Active", 70)))
        self.editions_grid = self._list(
            panel, (("Edition", 260), ("Year", 70), ("Cycle rotation", 150), ("Active", 70)),
        )
        self.cycles_grid = self._list(
            panel, (("Cycle", 250), ("Sequence", 90), ("Active", 70)),
        )
        body.Add(self._section(panel, "Local systems", self.systems,
                              (("Add", self.on_add_system), ("Edit", self.on_edit_system),
                               ("Retire / Restore", self.on_toggle_system))), 1, wx.EXPAND | wx.RIGHT, 8)
        right = wx.BoxSizer(wx.VERTICAL)
        right.Add(self._section(panel, "Editions", self.editions_grid,
                               (("Add", self.on_add_edition), ("Edit", self.on_edit_edition),
                                ("Retire / Restore", self.on_toggle_edition),
                                ("Propers...", self.on_propers))), 1, wx.EXPAND | wx.BOTTOM, 8)
        right.Add(self._section(panel, "Cycles", self.cycles_grid,
                               (("Add", self.on_add_cycle), ("Edit", self.on_edit_cycle),
                                ("Retire / Restore", self.on_toggle_cycle))), 1, wx.EXPAND)
        body.Add(right, 1, wx.EXPAND)
        outer.Add(body, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        close = wx.Button(panel, wx.ID_CLOSE, "Close"); close.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE))
        row = wx.BoxSizer(wx.HORIZONTAL); row.AddStretchSpacer(); row.Add(close)
        outer.Add(row, 0, wx.EXPAND | wx.ALL, 10); panel.SetSizer(outer)
        self.systems.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda _e: self.refresh_editions())
        self.systems.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_system)
        self.editions_grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_edition)
        self.editions_grid.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda _e: self.refresh_cycles())
        self.cycles_grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_cycle)
        self.refresh_systems(); self.CentreOnParent()

    @staticmethod
    def _list(parent, columns):
        control = wx.ListCtrl(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in columns: control.AppendColumn(label, width=width)
        return control

    @staticmethod
    def _section(parent, label, control, buttons):
        box = wx.StaticBoxSizer(wx.VERTICAL, parent, label); box.Add(control, 1, wx.EXPAND | wx.ALL, 6)
        row = wx.BoxSizer(wx.HORIZONTAL)
        for text, handler in buttons:
            button = wx.Button(parent, label=text); button.Bind(wx.EVT_BUTTON, handler); row.Add(button, 0, wx.RIGHT, 6)
        box.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 6); return box

    def refresh_systems(self, selected_id=None):
        self.system_rows = self.repository.systems(); self.systems.DeleteAllItems()
        select = -1
        for index, row in enumerate(self.system_rows):
            self.systems.InsertItem(index, str(row[1])); self.systems.SetItem(index, 1, str(row[2]))
            self.systems.SetItem(index, 2, "Yes" if row[3] else "No")
            if row[0] == selected_id: select = index
        if select < 0 and self.system_rows: select = 0
        if select >= 0: self.systems.Select(select)
        self.refresh_editions()

    def refresh_editions(self, selected_id=None):
        index = self.systems.GetFirstSelected(); self.editions_grid.DeleteAllItems()
        self.edition_rows = [] if index < 0 else self.repository.editions(self.system_rows[index][0])
        for pos, row in enumerate(self.edition_rows):
            self.editions_grid.InsertItem(pos, str(row[1])); self.editions_grid.SetItem(pos, 1, str(row[2] or ""))
            self.editions_grid.SetItem(pos, 2, str(row[3])); self.editions_grid.SetItem(pos, 3, "Yes" if row[4] else "No")
            if row[0] == selected_id: self.editions_grid.Select(pos)
        if self.edition_rows and self.editions_grid.GetFirstSelected() < 0:
            self.editions_grid.Select(0)
        self.refresh_cycles()

    def refresh_cycles(self, selected_id=None):
        index = self.editions_grid.GetFirstSelected(); self.cycles_grid.DeleteAllItems()
        self.cycle_rows = [] if index < 0 else self.repository.cycles(self.edition_rows[index][0])
        for pos, row in enumerate(self.cycle_rows):
            self.cycles_grid.InsertItem(pos, str(row[1]))
            self.cycles_grid.SetItem(pos, 1, str(row[2]))
            self.cycles_grid.SetItem(pos, 2, "Yes" if row[3] else "No")
            if row[0] == selected_id: self.cycles_grid.Select(pos)

    def _error(self, action):
        try: action()
        except Exception as error: wx.MessageBox(str(error), "Local Lectionary", wx.OK | wx.ICON_ERROR, self)

    def on_add_system(self, _event): self._edit_system(None)
    def on_edit_system(self, _event):
        index = self.systems.GetFirstSelected()
        if index >= 0: self._edit_system(self.system_rows[index])
    def _edit_system(self, row):
        dialog = _SystemDialog(self, row)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            self._error(lambda: self.refresh_systems(self.repository.save_system(
                row[0] if row else None, dialog.name.GetValue(), dialog.cycle.GetStringSelection(), dialog.note.GetValue())))
        finally: dialog.Destroy()
    def on_toggle_system(self, _event):
        index = self.systems.GetFirstSelected()
        if index >= 0:
            row = self.system_rows[index]; self._error(lambda: (self.repository.set_active("tblLectionarySystem", row[0], not row[3]), self.refresh_systems(row[0])))

    def on_add_edition(self, _event): self._edit_edition(None)
    def on_edit_edition(self, _event):
        index = self.editions_grid.GetFirstSelected()
        if index >= 0: self._edit_edition(self.edition_rows[index])
    def _edit_edition(self, row):
        system = self.systems.GetFirstSelected()
        if system < 0: return
        dialog = _EditionDialog(self, row)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            self._error(lambda: self.refresh_editions(self.repository.save_edition(
                row[0] if row else None, self.system_rows[system][0], dialog.name.GetValue(),
                dialog.year.GetValue(), dialog.rule.GetStringSelection(), dialog.note.GetValue())))
        finally: dialog.Destroy()
    def on_toggle_edition(self, _event):
        index = self.editions_grid.GetFirstSelected()
        if index >= 0:
            row = self.edition_rows[index]; self._error(lambda: (self.repository.set_active("tblLectionaryEdition", row[0], not row[4]), self.refresh_editions(row[0])))

    def on_propers(self, _event):
        index = self.editions_grid.GetFirstSelected()
        if index < 0: return
        dialog = _PropersDialog(self, self.repository, self.edition_rows[index])
        try: dialog.ShowModal()
        finally: dialog.Destroy()

    def on_add_cycle(self, _event): self._edit_cycle(None)
    def on_edit_cycle(self, _event):
        index = self.cycles_grid.GetFirstSelected()
        if index >= 0: self._edit_cycle(self.cycle_rows[index])
    def _edit_cycle(self, row):
        edition = self.editions_grid.GetFirstSelected()
        if edition < 0: return
        edition_id = self.edition_rows[edition][0]
        dialog = _CycleDialog(self, row)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            self._error(lambda: self.refresh_cycles(self.repository.save_cycle(
                row[0] if row else None, edition_id, dialog.name.GetValue(),
                dialog.sequence.GetValue())))
        finally: dialog.Destroy()
    def on_toggle_cycle(self, _event):
        edition = self.editions_grid.GetFirstSelected(); cycle = self.cycles_grid.GetFirstSelected()
        if edition >= 0 and cycle >= 0:
            row = self.cycle_rows[cycle]; edition_id = self.edition_rows[edition][0]
            self._error(lambda: (self.repository.set_cycle_active(
                row[0], edition_id, not row[3]), self.refresh_cycles(row[0])))


def show_local_lectionaries(parent, connection, authorization):
    """Open local lectionary maintenance."""
    dialog = LocalLectionaryDialog(parent, connection, authorization)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
