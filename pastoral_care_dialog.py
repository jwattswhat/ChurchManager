"""Native pastoral-care dashboard and safe operational history workflow."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import wx
import wx.adv
import JSForm

from pastoral_care_repository import MariaDBPastoralCareRepository
from pastoral_care_service import PastoralCareService


def _date_text(value):
    return value.strftime("%m/%d/%Y") if value else ""


def _wx_date(value=None):
    value = value or date.today()
    return wx.DateTime.FromDMY(value.day, value.month - 1, value.year)


def _python_date(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


def _due_group(record):
    today = date.today()
    due = record.get("next_follow_up_date") or record.get("due_date")
    if record.get("status") == "WAITING":
        return "Waiting"
    if due is None:
        return "No date"
    if due < today:
        return "Overdue"
    if due == today:
        return "Due today"
    if due <= today + timedelta(days=7):
        return "Due this week"
    return "Later"


def _selected_row_id(control):
    """Return the selected row ID, defaulting to the first visible row."""

    rows = getattr(control, "rows", ())
    if not rows:
        return None
    selection = control.GetSelection()
    return rows[selection if 0 <= selection < len(rows) else 0][0]


class NewCareNeedDialog(wx.Dialog):
    """Collect minimum-necessary safe fields for one new care need."""

    def __init__(self, parent, choices):
        super().__init__(parent, title="New Pastoral Follow-up", size=(620, 525))
        self.choices = choices
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        guidance = wx.StaticText(
            panel,
            label="Create a practical follow-up record. Do not enter confidential narrative here.",
        )
        guidance.SetForegroundColour(wx.Colour(0, 82, 155))
        outer.Add(guidance, 0, wx.ALL, 14)
        grid = wx.FlexGridSizer(cols=2, vgap=9, hgap=12)
        grid.AddGrowableCol(1, 1)
        self.church = self._choice(panel, choices["churches"])
        self.subject_type = wx.Choice(panel, choices=["Person", "Family", "Other"])
        self.subject_type.SetSelection(0)
        self.subject = wx.ComboBox(panel, style=wx.CB_DROPDOWN)
        self.category = wx.ComboBox(panel, choices=choices["categories"], style=wx.CB_DROPDOWN)
        self.assignee = self._choice(panel, [(None, "Unassigned")] + choices["users"])
        self.priority = wx.Choice(panel, choices=["Normal", "Urgent"])
        self.priority.SetSelection(0)
        self.opened = wx.adv.DatePickerCtrl(panel, dt=_wx_date())
        self.use_due = wx.CheckBox(panel, label="Set a due date")
        self.due = wx.adv.DatePickerCtrl(panel, dt=_wx_date())
        self.due.Enable(False)
        for label, control in (
            ("Church", self.church), ("Follow-up for", self.subject_type),
            ("Person, family, or brief subject", self.subject), ("Category", self.category),
            ("Assigned to", self.assignee), ("Priority", self.priority),
            ("Opened", self.opened), ("Due date", self.due),
        ):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        outer.Add(self.use_due, 0, wx.LEFT | wx.TOP, 14)
        outer.Add(wx.StaticText(panel, label="Safe summary (optional)"), 0, wx.LEFT | wx.TOP, 14)
        self.summary = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        outer.Add(self.summary, 1, wx.EXPAND | wx.ALL, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.AddStretchSpacer()
        save = wx.Button(panel, wx.ID_OK, "Create Follow-up")
        cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        buttons.Add(save, 0, wx.RIGHT, 8); buttons.Add(cancel)
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        panel.SetSizer(outer)
        self.subject_type.Bind(wx.EVT_CHOICE, self._load_subjects)
        self.use_due.Bind(wx.EVT_CHECKBOX, lambda _event: self.due.Enable(self.use_due.GetValue()))
        self._load_subjects()

    @staticmethod
    def _choice(parent, rows):
        control = wx.Choice(parent, choices=[row[1] for row in rows])
        control.rows = rows
        if rows:
            control.SetSelection(0)
        return control

    def _load_subjects(self, _event=None):
        kind = self.subject_type.GetStringSelection()
        rows = self.choices["people"] if kind == "Person" else self.choices["families"]
        self.subject.rows = rows if kind != "Other" else []
        self.subject.SetItems([row[1] for row in self.subject.rows])
        self.subject.SetValue(self.subject.rows[0][1] if self.subject.rows else "")

    def values(self):
        kind = self.subject_type.GetStringSelection()
        selected = self.subject.GetSelection()
        values = {
            "church_id": _selected_row_id(self.church),
            "church_name": self.church.GetStringSelection(),
            "category": self.category.GetValue(),
            "assigned_user_id": _selected_row_id(self.assignee),
            "priority": self.priority.GetStringSelection(),
            "opened_date": _python_date(self.opened),
            "due_date": _python_date(self.due) if self.use_due.GetValue() else None,
            "safe_summary": self.summary.GetValue(),
        }
        if kind == "Person" and selected >= 0:
            values["person_id"] = self.subject.rows[selected][0]
        elif kind == "Family" and selected >= 0:
            values["family_id"] = self.subject.rows[selected][0]
        else:
            values["display_subject"] = self.subject.GetValue()
        return values


class RecordCareActionDialog(wx.Dialog):
    """Collect a safe action outcome and optional next follow-up date."""

    def __init__(self, parent):
        super().__init__(parent, title="Record Pastoral Care Action", size=(540, 420))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=9, hgap=12); grid.AddGrowableCol(1, 1)
        self.action_type = wx.Choice(panel, choices=[
            "Call", "Visit", "Card", "Meal", "Email", "Prayer", "Referral", "Other"
        ]); self.action_type.SetSelection(0)
        self.result = wx.Choice(panel, choices=["Completed", "Attempted", "Deferred", "Not Needed"])
        self.result.SetSelection(0)
        self.use_follow_up = wx.CheckBox(panel, label="Set next follow-up")
        self.follow_up = wx.adv.DatePickerCtrl(panel, dt=_wx_date(date.today() + timedelta(days=7)))
        self.follow_up.Enable(False)
        for label, control in (("Action", self.action_type), ("Result", self.result),
                               ("Next follow-up", self.follow_up)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 0, wx.EXPAND | wx.ALL, 14)
        outer.Add(self.use_follow_up, 0, wx.LEFT | wx.RIGHT, 14)
        outer.Add(wx.StaticText(panel, label="Brief safe outcome (optional)"), 0, wx.ALL, 14)
        self.outcome = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        outer.Add(self.outcome, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_OK, "Record Action"), 0, wx.RIGHT, 8)
        buttons.Add(wx.Button(panel, wx.ID_CANCEL, "Cancel"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.use_follow_up.Bind(
            wx.EVT_CHECKBOX, lambda _event: self.follow_up.Enable(self.use_follow_up.GetValue())
        )

    def values(self):
        return {
            "action_type": self.action_type.GetStringSelection(),
            "result": self.result.GetStringSelection(),
            "action_datetime": datetime.now(),
            "safe_outcome": self.outcome.GetValue(),
            "next_follow_up_date": (
                _python_date(self.follow_up) if self.use_follow_up.GetValue() else None
            ),
        }


class CareHistoryDialog(wx.Dialog):
    """Show safe operational details and non-restricted action history."""

    def __init__(self, parent, service, care_need_id):
        super().__init__(parent, title="Pastoral Care History", size=(900, 620),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = service; self.care_need_id = care_need_id
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        self.heading = wx.StaticText(panel)
        font = self.heading.GetFont(); font.MakeBold(); font.SetPointSize(font.GetPointSize() + 2)
        self.heading.SetFont(font); outer.Add(self.heading, 0, wx.ALL, 12)
        self.details = wx.StaticText(panel); outer.Add(self.details, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Date and time", 145), ("Caregiver", 155), ("Action", 95),
            ("Result", 100), ("Safe outcome", 260), ("Next follow-up", 115),
        )):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        note = wx.StaticText(panel, label="Restricted notes are protected and are not available in this workflow yet.")
        note.SetForegroundColour(wx.Colour(110, 80, 0)); outer.Add(note, 0, wx.ALL, 12)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler, permission in (
            ("Record Action...", self.on_action, "pastoral.care.update"),
            ("Assign...", self.on_assign, "pastoral.care.assign"),
            ("Waiting", lambda e: self.on_status("WAITING"), "pastoral.care.close"),
            ("Complete", lambda e: self.on_status("COMPLETED"), "pastoral.care.close"),
            ("Close - Not Needed", lambda e: self.on_status("CLOSED_NOT_NEEDED"), "pastoral.care.close"),
            ("Reopen", lambda e: self.on_status("OPEN"), "pastoral.care.close"),
        ):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler)
            if self.service.authorization.has_permission(permission):
                buttons.Add(button, 0, wx.RIGHT, 7)
            else:
                button.Hide()
        buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12); panel.SetSizer(outer)
        self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.refresh()

    def refresh(self):
        self.record, rows = self.service.history(self.care_need_id)
        self.heading.SetLabel(self.record.get("display_subject") or "Pastoral follow-up")
        self.details.SetLabel(
            "Category: {category}    Assigned: {assigned}    Priority: {priority}    Status: {status}\n"
            "Opened: {opened}    Due: {due}    Next follow-up: {next_due}\n{summary}".format(
                category=self.record["category"], assigned=self.record.get("assignee") or "Unassigned",
                priority=self.record["priority"].title(), status=self.record["status"].replace("_", " ").title(),
                opened=_date_text(self.record["opened_date"]), due=_date_text(self.record.get("due_date")),
                next_due=_date_text(self.record.get("next_follow_up_date")),
                summary=self.record.get("safe_summary") or "",
            )
        )
        self.list.DeleteAllItems()
        for row in rows:
            index = self.list.InsertItem(self.list.GetItemCount(), row["action_datetime"].strftime("%m/%d/%Y %I:%M %p"))
            for column, value in enumerate((row["caregiver"], row["action_type"].title(),
                                            row["result"].replace("_", " ").title(),
                                            row.get("safe_outcome") or "",
                                            _date_text(row.get("next_follow_up_date"))), 1):
                self.list.SetItem(index, column, str(value))

    def on_action(self, _event):
        dialog = RecordCareActionDialog(self)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.service.record_action(self.care_need_id, dialog.values()); self.refresh()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Record Action", wx.OK | wx.ICON_ERROR, self)
        finally:
            dialog.Destroy()

    def on_assign(self, _event):
        try:
            rows = [(None, "Unassigned")] + self.service.choices()["users"]
            dialog = wx.SingleChoiceDialog(self, "Assign this follow-up to:", "Assign Pastoral Care",
                                           [row[1] for row in rows])
            if dialog.ShowModal() == wx.ID_OK:
                self.service.assign(self.care_need_id, rows[dialog.GetSelection()][0], self.record["version"])
                self.refresh()
            dialog.Destroy()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Assign Follow-up", wx.OK | wx.ICON_ERROR, self)

    def on_status(self, status):
        try:
            self.service.change_status(self.care_need_id, status, self.record["version"]); self.refresh()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Change Status", wx.OK | wx.ICON_ERROR, self)


class PastoralCareDashboard(wx.Dialog):
    """Display assigned or all open pastoral care using safe operational fields."""

    def __init__(self, parent, service, authorization):
        super().__init__(parent, title="Pastoral Care", size=(1050, 650),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = service; self.authorization = authorization; self.rows = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        header = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(panel, label="Pastoral Care Follow-ups")
        font = title.GetFont(); font.MakeBold(); font.SetPointSize(font.GetPointSize() + 3); title.SetFont(font)
        header.Add(title, 0, wx.ALIGN_CENTER_VERTICAL); header.AddStretchSpacer()
        self.scope = wx.Choice(panel, choices=["Assigned to Me"] + (
            ["All Open"] if authorization.has_permission("pastoral.care.view.all") else []
        )); self.scope.SetSelection(0); header.Add(self.scope, 0)
        outer.Add(header, 0, wx.EXPAND | wx.ALL, 14)
        guidance = wx.StaticText(panel, label="Double-click a row to review history or record the next action.")
        guidance.SetForegroundColour(wx.Colour(0, 82, 155)); outer.Add(guidance, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("When", 105), ("Subject", 220), ("Category", 145), ("Assignee", 160),
            ("Due", 100), ("Priority", 80), ("Status", 105),
        )):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        new = wx.Button(panel, label="New Follow-up..."); new.Bind(wx.EVT_BUTTON, self.on_new)
        open_button = wx.Button(panel, label="Open History"); open_button.Bind(wx.EVT_BUTTON, self.on_open)
        buttons.Add(new, 0, wx.RIGHT, 8); buttons.Add(open_button)
        buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        new.Show(authorization.has_permission("pastoral.care.create"))
        self.scope.Bind(wx.EVT_CHOICE, lambda _event: self.refresh())
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open)
        self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.refresh()

    def refresh(self):
        scope = "all" if self.scope.GetStringSelection() == "All Open" else "assigned"
        self.rows = self.service.work_list(scope)
        self.list.DeleteAllItems()
        for row in self.rows:
            due = row.get("next_follow_up_date") or row.get("due_date")
            index = self.list.InsertItem(self.list.GetItemCount(), _due_group(row))
            for column, value in enumerate((
                row.get("display_subject") or "(No subject)", row["category"],
                row.get("assignee") or "Unassigned", _date_text(due),
                row["priority"].title(), row["status"].replace("_", " ").title(),
            ), 1):
                self.list.SetItem(index, column, str(value))

    def on_open(self, _event):
        selected = self.list.GetFirstSelected()
        if selected < 0:
            wx.MessageBox("Select a pastoral follow-up first.", "Pastoral Care", wx.OK | wx.ICON_INFORMATION, self)
            return
        dialog = CareHistoryDialog(self, self.service, self.rows[selected]["id"])
        dialog.ShowModal(); dialog.Destroy(); self.refresh()

    def on_new(self, _event):
        submitted = {}
        try:
            dialog = NewCareNeedDialog(self, self.service.choices())
            if dialog.ShowModal() == wx.ID_OK:
                submitted = dialog.values()
                care_need_id = self.service.create_need(submitted)
                dialog.Destroy(); self.refresh()
                history = CareHistoryDialog(self, self.service, care_need_id)
                history.ShowModal(); history.Destroy()
                return
            dialog.Destroy()
        except Exception as error:
            JSForm.report_exception(
                error,
                operation="pastoral.create_follow_up",
                safe_context={
                    "church_id_type": type(submitted.get("church_id")).__name__,
                    "church_id_value": repr(submitted.get("church_id")),
                    "church_name": str(submitted.get("church_name") or ""),
                },
            )
            wx.MessageBox(str(error), "Unable to Create Follow-up", wx.OK | wx.ICON_ERROR, self)


def show_pastoral_care(parent, connection, session, authorization):
    """Open the permission-controlled pastoral-care dashboard."""

    repository = MariaDBPastoralCareRepository(connection)
    service = PastoralCareService(repository, session, authorization)
    dialog = PastoralCareDashboard(parent, service, authorization)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
