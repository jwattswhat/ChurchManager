"""User-facing editor for structured bulletin-order templates."""

from __future__ import annotations

import wx

from bulletin_orders import BulletinOrderRepository, render_plain_line


BLUE = wx.Colour(0, 90, 190)
LINE_TYPES = ("TEXT", "HEADING", "LITURGY", "HYMN", "READING", "SERMON", "OFFERING", "COMMUNION")
VALUE_SOURCES = ("", "SERVICE_HYMN", "SERVICE_READING")
CONDITIONS = ("ALWAYS", "COMMUNION", "NO_COMMUNION", "INCLUDE_SEASON", "EXCLUDE_SEASON", "USER_CHOICE")


class BulletinOrderLineDialog(wx.Dialog):
    def __init__(self, parent, existing=None, default_sequence=10):
        super().__init__(parent, title="Edit Bulletin Order Line", size=(600, 610))
        self.existing = existing
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        form = wx.FlexGridSizer(cols=2, vgap=8, hgap=12)
        form.AddGrowableCol(1, 1)

        self.sequence = wx.SpinCtrl(panel, min=1, max=99990, initial=default_sequence)
        self.line_type = wx.Choice(panel, choices=LINE_TYPES)
        self.line_type.SetStringSelection("TEXT")
        self.label = wx.TextCtrl(panel)
        self.value_source = wx.Choice(panel, choices=VALUE_SOURCES)
        self.value_source.SetSelection(0)
        self.value_key = wx.TextCtrl(panel)
        self.reference = wx.TextCtrl(panel)
        self.style = wx.Choice(panel, choices=("Normal", "Section Heading"))
        self.style.SetSelection(0)
        self.indent = wx.SpinCtrl(panel, min=0, max=6, initial=0)
        self.use_tab = wx.CheckBox(panel, label="Place the value at a tab stop")
        self.tab_position = wx.SpinCtrlDouble(panel, min=0.25, max=12.0, inc=0.25, initial=4.75)
        self.tab_alignment = wx.Choice(panel, choices=("LEFT", "CENTER", "RIGHT", "DECIMAL"))
        self.tab_alignment.SetStringSelection("RIGHT")
        self.tab_leader = wx.Choice(panel, choices=("NONE", "DOTS", "LINE"))
        self.tab_leader.SetSelection(0)
        self.condition = wx.Choice(panel, choices=CONDITIONS)
        self.condition.SetSelection(0)
        self.condition_value = wx.TextCtrl(panel)
        self.note = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.note.SetMinSize((-1, 75))

        for text, control in (
            ("Order", self.sequence), ("Line type", self.line_type),
            ("Bulletin text", self.label), ("Insert value from", self.value_source),
            ("Value name", self.value_key), ("Reference or page", self.reference),
            ("Paragraph style", self.style), ("Indent level", self.indent),
        ):
            form.Add(wx.StaticText(panel, label=text), 0, wx.ALIGN_CENTER_VERTICAL)
            form.Add(control, 1, wx.EXPAND)

        format_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Alignment and formatting")
        format_box.Add(self.use_tab, 0, wx.ALL, 4)
        tab_row = wx.BoxSizer(wx.HORIZONTAL)
        tab_row.Add(wx.StaticText(panel, label="Position (inches)"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        tab_row.Add(self.tab_position, 0, wx.RIGHT, 12)
        tab_row.Add(wx.StaticText(panel, label="Alignment"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        tab_row.Add(self.tab_alignment, 0, wx.RIGHT, 12)
        tab_row.Add(wx.StaticText(panel, label="Leader"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        tab_row.Add(self.tab_leader, 0)
        format_box.Add(tab_row, 0, wx.ALL, 4)
        emphasis = wx.BoxSizer(wx.HORIZONTAL)
        self.label_bold = wx.CheckBox(panel, label="Bold label")
        self.value_bold = wx.CheckBox(panel, label="Bold inserted value")
        self.italic = wx.CheckBox(panel, label="Italic")
        for control in (self.label_bold, self.value_bold, self.italic):
            emphasis.Add(control, 0, wx.RIGHT, 18)
        format_box.Add(emphasis, 0, wx.ALL, 4)

        condition_form = wx.FlexGridSizer(cols=2, vgap=8, hgap=12)
        condition_form.AddGrowableCol(1, 1)
        condition_form.Add(wx.StaticText(panel, label="Include condition"), 0, wx.ALIGN_CENTER_VERTICAL)
        condition_form.Add(self.condition, 1, wx.EXPAND)
        condition_form.Add(wx.StaticText(panel, label="Season or choice"), 0, wx.ALIGN_CENTER_VERTICAL)
        condition_form.Add(self.condition_value, 1, wx.EXPAND)
        condition_form.Add(wx.StaticText(panel, label="Internal note"), 0, wx.ALIGN_TOP)
        condition_form.Add(self.note, 1, wx.EXPAND)

        buttons = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        outer.Add(form, 0, wx.EXPAND | wx.ALL, 12)
        outer.Add(format_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        outer.Add(condition_form, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(outer)
        self.use_tab.Bind(wx.EVT_CHECKBOX, self._tab_state)
        if existing:
            self._load(existing)
        self._tab_state()

    def _load(self, row):
        self.sequence.SetValue(row[1])
        self.line_type.SetStringSelection(row[2])
        self.label.SetValue(row[3] or "")
        self.value_source.SetStringSelection(row[4] or "")
        self.value_key.SetValue(row[5] or "")
        self.reference.SetValue(row[6] or "")
        self.style.SetStringSelection(row[7] or "Normal")
        self.label_bold.SetValue(bool(row[8]))
        self.value_bold.SetValue(bool(row[9]))
        self.italic.SetValue(bool(row[10]))
        self.indent.SetValue(int(row[11] or 0))
        self.use_tab.SetValue(row[12] is not None)
        self.tab_position.SetValue(float(row[12] or 4.75))
        self.tab_alignment.SetStringSelection(row[13] or "RIGHT")
        self.tab_leader.SetStringSelection(row[14] or "NONE")
        self.condition.SetStringSelection(row[15] or "ALWAYS")
        self.condition_value.SetValue(row[16] or "")
        self.note.SetValue(row[17] or "")

    def _tab_state(self, _event=None):
        enabled = self.use_tab.GetValue()
        for control in (self.tab_position, self.tab_alignment, self.tab_leader):
            control.Enable(enabled)

    def values(self):
        label = self.label.GetValue().strip()
        if not label:
            raise ValueError("Enter the bulletin text for this line.")
        return {
            "Sequence": self.sequence.GetValue(), "LineType": self.line_type.GetStringSelection(),
            "Label": label, "ValueSource": self.value_source.GetStringSelection() or None,
            "ValueKey": self.value_key.GetValue().strip() or None,
            "ReferenceText": self.reference.GetValue().strip() or None,
            "StyleName": self.style.GetStringSelection(), "LabelBold": self.label_bold.GetValue(),
            "ValueBold": self.value_bold.GetValue(), "Italic": self.italic.GetValue(),
            "IndentLevel": self.indent.GetValue(),
            "TabPosition": self.tab_position.GetValue() if self.use_tab.GetValue() else None,
            "TabAlignment": self.tab_alignment.GetStringSelection(),
            "TabLeader": self.tab_leader.GetStringSelection(),
            "ConditionType": self.condition.GetStringSelection(),
            "ConditionValue": self.condition_value.GetValue().strip() or None,
            "Note": self.note.GetValue().strip() or None,
        }


class BulletinOrderDialog(wx.Dialog):
    def __init__(self, parent, connection, church_id=None):
        super().__init__(parent, title="Bulletin Order Templates", size=(1120, 700),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = BulletinOrderRepository(connection)
        self.church_id = church_id
        self.template_rows = []
        self.line_rows = []
        self._build()
        self.refresh_templates()
        self.CentreOnParent()

    def _build(self):
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        help_text = wx.StaticText(
            panel,
            label="Choose a bulletin-order template. Blue entries are customized; starter templates are protected.",
        )
        help_text.SetForegroundColour(BLUE)
        outer.Add(help_text, 0, wx.ALL, 10)
        body = wx.BoxSizer(wx.HORIZONTAL)
        self.templates = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.templates.AppendColumn("Template", width=245)
        self.templates.AppendColumn("Status", width=90)
        self.lines = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Order", 65), ("Bulletin text", 300), ("Reference / value", 190),
                             ("Type", 100), ("Condition", 135), ("Review", 70)):
            self.lines.AppendColumn(label, width=width)
        body.Add(self.templates, 0, wx.EXPAND | wx.RIGHT, 10)
        body.Add(self.lines, 1, wx.EXPAND)
        outer.Add(body, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        specs = (
            ("Duplicate Template", self.on_duplicate), ("Delete Custom", self.on_delete_template),
            ("Add Line", self.on_add), ("Edit Line", self.on_edit), ("Delete Line", self.on_delete_line),
            ("Move Up", lambda event: self.on_move(-1)), ("Move Down", lambda event: self.on_move(1)),
            ("Preview Plain Text", self.on_preview),
        )
        for label, handler in specs:
            button = wx.Button(panel, label=label)
            button.Bind(wx.EVT_BUTTON, handler)
            buttons.Add(button, 0, wx.RIGHT, 6)
        buttons.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)
        self.templates.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_template_selected)
        self.lines.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit)

    def refresh_templates(self, select_id=None):
        self.template_rows = self.repository.templates()
        self.templates.DeleteAllItems()
        selected_index = 0
        for index, row in enumerate(self.template_rows):
            item = self.templates.InsertItem(index, row[1])
            self.templates.SetItem(item, 1, "Starter" if row[4] else "Customized")
            if not row[4]:
                self.templates.SetItemTextColour(item, BLUE)
            if row[0] == select_id:
                selected_index = index
        if self.template_rows:
            self.templates.Select(selected_index)
            self.templates.Focus(selected_index)

    def selected_template(self):
        index = self.templates.GetFirstSelected()
        return None if index < 0 else self.template_rows[index]

    def selected_line(self):
        index = self.lines.GetFirstSelected()
        return None if index < 0 else self.line_rows[index]

    def on_template_selected(self, _event=None):
        template = self.selected_template()
        self.line_rows = self.repository.lines(template[0]) if template else []
        self.lines.DeleteAllItems()
        for index, row in enumerate(self.line_rows):
            item = self.lines.InsertItem(index, str(row[1]))
            value = row[5] or row[6] or ""
            for column, text in enumerate((row[3], value, row[2], row[15], "Yes" if row[18] else ""), 1):
                self.lines.SetItem(item, column, str(text or ""))

    def _require_custom(self):
        template = self.selected_template()
        if not template:
            raise ValueError("Select a bulletin-order template.")
        if template[4]:
            raise ValueError("Duplicate this starter template before editing it.")
        return template

    def on_duplicate(self, _event):
        template = self.selected_template()
        if not template:
            return
        dialog = wx.TextEntryDialog(self, "Name for the customized copy:", "Duplicate Bulletin Order",
                                    value=template[1] + " - Custom")
        try:
            if dialog.ShowModal() == wx.ID_OK and dialog.GetValue().strip():
                new_id = self.repository.duplicate_template(template[0], dialog.GetValue(), self.church_id)
                self.refresh_templates(new_id)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to duplicate", wx.OK | wx.ICON_ERROR, self)
        finally:
            dialog.Destroy()

    def on_delete_template(self, _event):
        try:
            template = self._require_custom()
            if wx.MessageBox(f"Delete the customized template '{template[1]}'?", "Delete Custom Template",
                             wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) == wx.YES:
                self.repository.delete_custom_template(template[0])
                self.refresh_templates()
        except Exception as error:
            wx.MessageBox(str(error), "Protected template", wx.OK | wx.ICON_INFORMATION, self)

    def on_add(self, _event):
        try:
            template = self._require_custom()
            default_sequence = (self.line_rows[-1][1] + 10) if self.line_rows else 10
            dialog = BulletinOrderLineDialog(self, default_sequence=default_sequence)
            try:
                if dialog.ShowModal() == wx.ID_OK:
                    self.repository.save_line(template[0], dialog.values())
                    self.on_template_selected()
            finally:
                dialog.Destroy()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to add line", wx.OK | wx.ICON_ERROR, self)

    def on_edit(self, _event):
        try:
            template = self._require_custom()
            line = self.selected_line()
            if not line:
                return
            dialog = BulletinOrderLineDialog(self, existing=line)
            try:
                if dialog.ShowModal() == wx.ID_OK:
                    self.repository.save_line(template[0], dialog.values(), line[0])
                    self.on_template_selected()
            finally:
                dialog.Destroy()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to edit line", wx.OK | wx.ICON_ERROR, self)

    def on_delete_line(self, _event):
        try:
            template = self._require_custom()
            line = self.selected_line()
            if line and wx.MessageBox("Delete the selected bulletin line?", "Delete Line",
                                      wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) == wx.YES:
                self.repository.delete_line(template[0], line[0])
                self.on_template_selected()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to delete line", wx.OK | wx.ICON_ERROR, self)

    def on_move(self, direction):
        try:
            template = self._require_custom()
            line = self.selected_line()
            if line:
                self.repository.move_line(template[0], line[0], direction)
                self.on_template_selected()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to move line", wx.OK | wx.ICON_ERROR, self)

    def on_preview(self, _event):
        if not self.line_rows:
            return
        text = "\r\n".join(
            render_plain_line(row[3], reference=row[6], indent_level=row[11], has_tab=row[12] is not None)
            for row in self.line_rows
        )
        dialog = wx.Dialog(self, title="Plain-Text Template Preview", size=(700, 600),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        panel = wx.Panel(dialog)
        sizer = wx.BoxSizer(wx.VERTICAL)
        preview = wx.TextCtrl(panel, value=text, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        preview.SetFont(wx.Font(wx.FontInfo(10).Family(wx.FONTFAMILY_TELETYPE)))
        sizer.Add(preview, 1, wx.EXPAND | wx.ALL, 10)
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: dialog.EndModal(wx.ID_CLOSE))
        sizer.Add(close, 0, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)
        dialog.ShowModal()
        dialog.Destroy()


def show_bulletin_orders(parent, connection, church_id=None):
    dialog = BulletinOrderDialog(parent, connection, church_id)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
