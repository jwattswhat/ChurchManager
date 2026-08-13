"""Enter service-specific values without changing a reusable bulletin template."""

from __future__ import annotations

import wx

from bulletin_orders import BulletinOrderGenerator, WeeklyBulletinOrderRepository


class WeeklyLineDialog(wx.Dialog):
    def __init__(self, parent, row):
        super().__init__(parent, title="Weekly Bulletin Line", size=(560, 410))
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        form = wx.FlexGridSizer(cols=2, vgap=9, hgap=12)
        form.AddGrowableCol(1, 1)
        self.included = wx.CheckBox(panel, label="Include this line in this service")
        self.included.SetValue(bool(row[2]))
        self.label = wx.TextCtrl(panel, value=row[4] or "")
        self.value = wx.TextCtrl(panel, value=row[7] or "")
        self.reference = wx.TextCtrl(panel, value=row[8] or "")
        self.note = wx.TextCtrl(panel, value=row[17] or "", style=wx.TE_MULTILINE)
        self.note.SetMinSize((-1, 90))
        form.Add(wx.StaticText(panel, label="Use this week"), 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self.included, 1, wx.EXPAND)
        form.Add(wx.StaticText(panel, label="Bulletin text"), 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self.label, 1, wx.EXPAND)
        source = row[6] or row[5] or "Fixed line"
        form.Add(wx.StaticText(panel, label="Expected value"), 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(wx.StaticText(panel, label=str(source)))
        form.Add(wx.StaticText(panel, label="This week's value"), 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self.value, 1, wx.EXPAND)
        form.Add(wx.StaticText(panel, label="Reference or page"), 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self.reference, 1, wx.EXPAND)
        form.Add(wx.StaticText(panel, label="Weekly note"), 0, wx.ALIGN_TOP)
        form.Add(self.note, 1, wx.EXPAND)
        outer.Add(form, 1, wx.EXPAND | wx.ALL, 12)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.AddStretchSpacer()
        save = wx.Button(panel, wx.ID_OK, "Save")
        cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        save.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK))
        cancel.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CANCEL))
        buttons.Add(save, 0, wx.RIGHT, 8)
        buttons.Add(cancel, 0)
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer)
        self.SetAffirmativeId(wx.ID_OK)
        self.SetEscapeId(wx.ID_CANCEL)

    def values(self):
        label = self.label.GetValue().strip()
        if not label:
            raise ValueError("Enter the bulletin text for this line.")
        return (
            self.included.GetValue(), label, self.value.GetValue().strip(),
            self.reference.GetValue().strip(), self.note.GetValue().strip(),
        )


class WeeklyBulletinOrderDialog(wx.Dialog):
    def __init__(self, parent, connection):
        super().__init__(parent, title="Weekly Bulletin Order", size=(1060, 700),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.generator = BulletinOrderGenerator(connection)
        self.repository = WeeklyBulletinOrderRepository(connection)
        self.service_rows = self.generator.services()
        self.template_rows = [row for row in self.generator.repository.templates() if row[3]]
        self.line_rows = []
        self._build()
        self._load_choices()
        self.CentreOnParent()

    def _build(self):
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        help_text = wx.StaticText(
            panel,
            label=(
                "Choose this week's service and apply a template once. Double-click a line to "
                "enter this week's outline value, include it, or omit it. This produces an outline, "
                "not the full service text. The template is not changed."
            ),
        )
        help_text.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(help_text, 0, wx.ALL, 10)
        choices = wx.FlexGridSizer(cols=2, vgap=8, hgap=12)
        choices.AddGrowableCol(1, 1)
        self.service = wx.Choice(panel)
        self.template = wx.Choice(panel)
        choices.Add(wx.StaticText(panel, label="Service"), 0, wx.ALIGN_CENTER_VERTICAL)
        choices.Add(self.service, 1, wx.EXPAND)
        choices.Add(wx.StaticText(panel, label="Template"), 0, wx.ALIGN_CENTER_VERTICAL)
        choices.Add(self.template, 1, wx.EXPAND)
        outer.Add(choices, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Use", 50), ("Order", 65), ("Bulletin text", 330),
                             ("This week's value", 220), ("Reference", 120), ("Type", 100)):
            self.grid.AppendColumn(label, width=width)
        outer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.status = wx.StaticText(panel, label="Select a service.")
        outer.Add(self.status, 0, wx.ALL, 10)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("Apply Selected Template", self.on_apply),
                               ("Edit Weekly Line", self.on_edit),
                               ("Move Up", lambda _event: self.on_move(-1)),
                               ("Move Down", lambda _event: self.on_move(1))):
            button = wx.Button(panel, label=label)
            button.Bind(wx.EVT_BUTTON, handler)
            buttons.Add(button, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)
        self.service.Bind(wx.EVT_CHOICE, self.on_service)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit)

    def _load_choices(self):
        for row in self.service_rows:
            when = row[1].strftime("%m/%d/%Y %I:%M %p") if hasattr(row[1], "strftime") else str(row[1])
            self.service.Append(f"{when} — {row[2] or 'Service'}")
        for row in self.template_rows:
            self.template.Append(row[1] + (" (Starter)" if row[4] else " (Customized)"))
        if self.service_rows:
            self.service.SetSelection(0)
            self.on_service()

    def selected_service_id(self):
        index = self.service.GetSelection()
        return None if index < 0 else self.service_rows[index][0]

    def on_service(self, _event=None):
        service_id = self.selected_service_id()
        assignment = self.repository.assignment(service_id) if service_id is not None else None
        if assignment:
            template_index = next(
                (index for index, row in enumerate(self.template_rows) if row[0] == assignment[1]), 0
            )
            if self.template_rows:
                self.template.SetSelection(template_index)
        else:
            suggested = self.generator.suggested_template_id(service_id) if service_id is not None else None
            template_index = next(
                (index for index, row in enumerate(self.template_rows) if row[0] == suggested), 0
            )
            if self.template_rows:
                self.template.SetSelection(template_index)
        self.refresh_lines()

    def refresh_lines(self):
        service_id = self.selected_service_id()
        self.line_rows = self.repository.lines(service_id) if service_id is not None else []
        assignment = self.repository.assignment(service_id) if service_id is not None else None
        missing_ids = set()
        if assignment and self.line_rows:
            rendered = self.generator.render(assignment[1], service_id)
            missing_ids = {item["id"] for item in rendered["lines"] if item["missing"]}
        self.grid.DeleteAllItems()
        for index, row in enumerate(self.line_rows):
            item = self.grid.InsertItem(index, "Yes" if row[2] else "No")
            for column, value in enumerate((row[1], row[4], row[7] or "", row[8] or "", row[3]), 1):
                self.grid.SetItem(item, column, str(value))
            if not row[2]:
                self.grid.SetItemTextColour(item, wx.Colour(120, 120, 120))
            elif row[0] in missing_ids:
                self.grid.SetItemTextColour(item, wx.RED)
        if self.line_rows:
            missing = len(missing_ids)
            self.status.SetLabel(
                f"{len(self.line_rows)} weekly line(s). "
                + (f"{missing} unfinished line(s) are shown in red."
                   if missing else "All required outline values are complete.")
            )
        else:
            self.status.SetLabel("No weekly order exists. Choose a template and select Apply Selected Template.")

    def on_apply(self, _event):
        service_id, template_index = self.selected_service_id(), self.template.GetSelection()
        if service_id is None or template_index < 0:
            return
        if self.line_rows and wx.MessageBox(
            "Applying the template again will replace this service's weekly entries. Continue?",
            "Replace Weekly Bulletin Order", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        ) != wx.YES:
            return
        try:
            count = self.repository.apply_template(service_id, self.template_rows[template_index][0])
            self.refresh_lines()
            self.status.SetLabel(f"Created this week's order with {count} line(s).")
        except Exception as error:
            wx.MessageBox(str(error), "Unable to apply template", wx.OK | wx.ICON_ERROR, self)

    def selected_line(self):
        index = self.grid.GetFirstSelected()
        return None if index < 0 else self.line_rows[index]

    def on_edit(self, _event):
        row = self.selected_line()
        service_id = self.selected_service_id()
        if not row or service_id is None:
            return
        dialog = WeeklyLineDialog(self, row)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.repository.save_line(service_id, row[0], *dialog.values())
                self.refresh_lines()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to save weekly line", wx.OK | wx.ICON_ERROR, self)
        finally:
            dialog.Destroy()

    def on_move(self, direction):
        row = self.selected_line()
        service_id = self.selected_service_id()
        if row and service_id is not None:
            self.repository.move_line(service_id, row[0], direction)
            self.refresh_lines()


def show_weekly_bulletin_order(parent, connection):
    dialog = WeeklyBulletinOrderDialog(parent, connection)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
