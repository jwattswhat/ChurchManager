"""Preview and apply annual envelope-box assignments without rewriting history."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import wx

from bulletin_orders import portable_connection
from giving.validation import GivingValidationError


ASSIGN_NEW_SEQUENCE = "NEW_SEQUENCE"
KEEP_CURRENT_NUMBERS = "KEEP_CURRENT"


@dataclass(frozen=True)
class EnvelopeAssignmentPlanRow:
    """One contributor's proposed annual envelope assignment."""

    contributor_id: int
    contributor_name: str
    current_number: str | None
    proposed_number: str
    result: str


def assign_annual_numbers(contributors, current_numbers, strategy, first_number=1):
    """Return deterministic annual assignments for already sorted contributors."""
    first_number = int(first_number)
    if first_number < 1:
        raise GivingValidationError("The first envelope number must be positive.")
    if strategy not in (ASSIGN_NEW_SEQUENCE, KEEP_CURRENT_NUMBERS):
        raise GivingValidationError("Select a valid annual assignment strategy.")
    rows = []
    used = set()
    if strategy == KEEP_CURRENT_NUMBERS:
        for contributor_id, _name in contributors:
            raw = current_numbers.get(contributor_id)
            if raw is None:
                continue
            normalized = str(int(raw)) if str(raw).isdecimal() else str(raw).strip()
            identity = (("N", int(normalized)) if normalized.isdecimal()
                        else ("T", normalized.casefold()))
            if identity in used:
                raise GivingValidationError(
                    "Current envelope assignments contain a duplicate number. Resolve it before continuing."
                )
            used.add(identity)
    next_number = first_number
    for contributor_id, name in contributors:
        current = current_numbers.get(contributor_id)
        if strategy == KEEP_CURRENT_NUMBERS and current is not None:
            proposed = str(int(current)) if str(current).isdecimal() else str(current).strip()
            result = "Retained"
        else:
            while ("N", next_number) in used:
                next_number += 1
            proposed = str(next_number)
            used.add(("N", next_number))
            next_number += 1
            result = "Assigned"
        rows.append(EnvelopeAssignmentPlanRow(
            contributor_id, name, str(current) if current is not None else None,
            proposed, result,
        ))
    return rows


class AnnualEnvelopeAssignmentService:
    """Build and atomically apply one calendar year's envelope assignments."""

    def __init__(self, connection, user_id):
        self.connection = portable_connection(connection)
        self.user_id = user_id

    def _all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def church_id(self):
        rows = self._all("SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
        if not rows:
            raise GivingValidationError("Church information must be created first.")
        return rows[0][0]

    @staticmethod
    def period(year):
        year = int(year)
        if year < 1900 or year > 9998:
            raise GivingValidationError("Enter a valid assignment year.")
        return date(year, 1, 1), date(year, 12, 31)

    def preview(self, year, strategy, first_number=1):
        """Return the proposed rows after validating target-year conflicts."""
        start, through = self.period(year)
        church_id = self.church_id()
        existing = self._all(
            "SELECT COUNT(*) FROM tblContributionEnvelopeAssignment "
            "WHERE ChurchID=? AND EffectiveFrom>=? AND EffectiveFrom<=?",
            (church_id, start, through),
        )[0][0]
        if existing:
            raise GivingValidationError(
                f"Envelope assignments already begin in {year}. This tool will not replace them."
            )
        contributors = self._all(
            "SELECT ID,DisplayName FROM tblContributionContributor "
            "WHERE ChurchID=? AND IsActive=1 ORDER BY DisplayName,ID", (church_id,),
        )
        if not contributors:
            raise GivingValidationError("There are no active contributors to assign.")
        prior_day = date(int(year) - 1, 12, 31)
        current_rows = self._all(
            "SELECT ContributorID,EnvelopeNumber FROM tblContributionEnvelopeAssignment "
            "WHERE ChurchID=? AND EffectiveFrom<=? "
            "AND COALESCE(EffectiveThrough,'9999-12-31')>=? "
            "ORDER BY ContributorID,EffectiveFrom DESC,ID DESC",
            (church_id, prior_day, prior_day),
        )
        current = {}
        for contributor_id, number in current_rows:
            if contributor_id in current:
                raise GivingValidationError(
                    "A contributor has overlapping current envelope assignments. Resolve it before continuing."
                )
            current[contributor_id] = number
        return assign_annual_numbers(contributors, current, strategy, first_number)

    def apply(self, year, strategy, first_number, expected_rows):
        """Rebuild the preview and apply that exact plan as one audited transaction."""
        rows = self.preview(year, strategy, first_number)
        if rows != list(expected_rows):
            raise GivingValidationError(
                "Contributor or envelope data changed after preview. Preview the assignments again."
            )
        start, through = self.period(year)
        previous_day = date(int(year) - 1, 12, 31)
        church_id = self.church_id()
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblContributionEnvelopeAssignment SET EffectiveThrough=? "
                "WHERE ChurchID=? AND EffectiveFrom<? "
                "AND COALESCE(EffectiveThrough,'9999-12-31')>=?",
                (previous_day, church_id, start, start),
            )
            note = f"Annual assignment for {year}"
            for row in rows:
                cursor.execute(
                    "INSERT INTO tblContributionEnvelopeAssignment "
                    "(ChurchID,ContributorID,EnvelopeNumber,EffectiveFrom,EffectiveThrough,Note) "
                    "VALUES (?,?,?,?,?,?)",
                    (church_id, row.contributor_id, row.proposed_number, start, through, note),
                )
            cursor.execute(
                "INSERT INTO tblContributionAuditEvent "
                "(ChurchID,UserID,Action,EntityType,SafeReference) VALUES (?,?,?,?,?)",
                (church_id, self.user_id, "ANNUAL_ENVELOPES_ASSIGNED", "ENVELOPE_ASSIGNMENT",
                 f"{year}; {strategy}; {len(rows)} assignments"),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
        return rows


class AnnualEnvelopeAssignmentDialog(wx.Dialog):
    """Show a complete annual assignment preview before enabling Apply."""

    STRATEGIES = (
        ("Assign a new sequence", ASSIGN_NEW_SEQUENCE),
        ("Keep current numbers and fill gaps", KEEP_CURRENT_NUMBERS),
    )

    def __init__(self, parent, connection, user_id):
        super().__init__(parent, title="Annual Envelope Assignment", size=(850, 650),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = AnnualEnvelopeAssignmentService(connection, user_id)
        self.preview_rows = []
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        heading = wx.StaticText(panel, label="Prepare Annual Envelope Boxes")
        heading.SetFont(heading.GetFont().Bold().Larger())
        outer.Add(heading, 0, wx.LEFT | wx.TOP, 14)
        outer.Add(wx.StaticText(
            panel, label="Preview every assignment before applying it. Prior years remain unchanged."
        ), 0, wx.LEFT | wx.TOP | wx.BOTTOM, 14)
        options = wx.FlexGridSizer(0, 2, 8, 12)
        options.AddGrowableCol(1, 1)
        self.year = wx.SpinCtrl(panel, min=1900, max=9998, initial=date.today().year + 1)
        self.strategy = wx.Choice(panel, choices=[item[0] for item in self.STRATEGIES])
        self.strategy.SetSelection(1)
        self.first_number = wx.SpinCtrl(panel, min=1, max=999999, initial=1)
        for label, control in (("Assignment year", self.year), ("Numbering method", self.strategy),
                               ("First available number", self.first_number)):
            options.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            options.Add(control, 1, wx.EXPAND)
        outer.Add(options, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Contributor", 330), ("Current", 100), ("Proposed", 100), ("Result", 120),
        )):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.ALL, 14)
        self.summary = wx.StaticText(panel, label="Select Preview to calculate the annual assignments.")
        outer.Add(self.summary, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        preview = wx.Button(panel, label="Preview Assignments")
        preview.Bind(wx.EVT_BUTTON, self.on_preview)
        self.apply_button = wx.Button(panel, label="Apply Preview")
        self.apply_button.Enable(False)
        self.apply_button.Bind(wx.EVT_BUTTON, self.on_apply)
        close = wx.Button(panel, wx.ID_CLOSE)
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons.Add(preview, 0, wx.RIGHT, 8)
        buttons.Add(self.apply_button, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer()
        buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        panel.SetSizer(outer)
        self.year.Bind(wx.EVT_SPINCTRL, self.on_option_changed)
        self.strategy.Bind(wx.EVT_CHOICE, self.on_option_changed)
        self.first_number.Bind(wx.EVT_SPINCTRL, self.on_option_changed)

    def selected_strategy(self):
        return self.STRATEGIES[self.strategy.GetSelection()][1]

    def on_option_changed(self, _event=None):
        self.preview_rows = []
        self.apply_button.Enable(False)
        self.summary.SetLabel("Options changed. Preview the assignments again.")

    def on_preview(self, _event=None):
        try:
            self.preview_rows = self.service.preview(
                self.year.GetValue(), self.selected_strategy(), self.first_number.GetValue()
            )
            self.list.DeleteAllItems()
            for index, row in enumerate(self.preview_rows):
                self.list.InsertItem(index, row.contributor_name)
                self.list.SetItem(index, 1, row.current_number or "Unassigned")
                self.list.SetItem(index, 2, row.proposed_number)
                self.list.SetItem(index, 3, row.result)
            numeric = [int(row.proposed_number) for row in self.preview_rows
                       if row.proposed_number.isdecimal()]
            highest = max(numeric) if numeric else 0
            assigned = sum(row.result == "Assigned" for row in self.preview_rows)
            retained = len(self.preview_rows) - assigned
            self.summary.SetLabel(
                f"{len(self.preview_rows)} contributors · {retained} retained · "
                f"{assigned} assigned · highest numeric box {highest}"
            )
            self.apply_button.Enable(True)
        except Exception as error:
            self.preview_rows = []
            self.apply_button.Enable(False)
            wx.MessageBox(str(error), "Unable to Preview Assignments", wx.OK | wx.ICON_ERROR, self)

    def on_apply(self, _event=None):
        if not self.preview_rows:
            return
        year = self.year.GetValue()
        if wx.MessageBox(
            f"Apply these {len(self.preview_rows)} envelope assignments for {year}?\n\n"
            "Prior assignments will end on December 31 of the preceding year.",
            "Apply Annual Envelope Assignments",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        ) != wx.YES:
            return
        try:
            self.service.apply(
                year, self.selected_strategy(), self.first_number.GetValue(), self.preview_rows
            )
            wx.MessageBox(f"The {year} envelope assignments were created.",
                          "Annual Assignment Complete", wx.OK | wx.ICON_INFORMATION, self)
            self.EndModal(wx.ID_OK)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Apply Assignments", wx.OK | wx.ICON_ERROR, self)


def show_annual_envelope_assignment(parent, connection, user_id):
    """Open the guarded annual envelope assignment workflow."""
    dialog = AnnualEnvelopeAssignmentDialog(parent, connection, user_id)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
