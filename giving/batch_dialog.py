"""Confidential draft contribution-batch entry dialogs."""

from datetime import date

import wx
import wx.adv

from giving.batch_service import DraftBatchService
from giving.validation import GivingValidationError


def _date(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


def _dialog_buttons(panel):
    """Create panel-owned OK and Cancel buttons for a panel-owned sizer."""
    buttons = wx.StdDialogButtonSizer()
    buttons.AddButton(wx.Button(panel, wx.ID_OK))
    buttons.AddButton(wx.Button(panel, wx.ID_CANCEL))
    buttons.Realize()
    return buttons


class NewBatchDialog(wx.Dialog):
    """Collect the small header required to begin a draft batch."""

    def __init__(self, parent, organizations):
        super().__init__(parent, title="New Contribution Batch", size=(560, 330))
        self.organizations = organizations
        panel = wx.Panel(self); form = wx.FlexGridSizer(0, 2, 9, 10); form.AddGrowableCol(1, 1)
        self.batch_date = wx.adv.DatePickerCtrl(panel)
        self.description = wx.TextCtrl(panel)
        self.organization = wx.Choice(panel, choices=[row[1] for row in organizations])
        self.control = wx.TextCtrl(panel)
        self.deposit = wx.adv.DatePickerCtrl(panel)
        self.has_deposit = wx.CheckBox(panel, label="Deposit date is known")
        for label, control in (("Batch date", self.batch_date), ("Description", self.description),
                               ("Accounting organization", self.organization),
                               ("Expected/control total", self.control), ("", self.has_deposit),
                               ("Deposit date", self.deposit)):
            form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            form.Add(control, 1, wx.EXPAND)
        self.organization.SetSelection(0 if organizations else wx.NOT_FOUND)
        self.deposit.Enable(False)
        self.has_deposit.Bind(wx.EVT_CHECKBOX, lambda _e: self.deposit.Enable(self.has_deposit.GetValue()))
        buttons = _dialog_buttons(panel)
        outer = wx.BoxSizer(wx.VERTICAL); outer.Add(form, 1, wx.EXPAND | wx.ALL, 14)
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)

    def values(self):
        selected = self.organization.GetSelection()
        if selected < 0:
            raise GivingValidationError("An accounting organization is required.")
        return dict(batch_date=_date(self.batch_date), description=self.description.GetValue(),
                    organization_id=self.organizations[selected][0],
                    control_total=self.control.GetValue().strip() or None,
                    deposit_date=_date(self.deposit) if self.has_deposit.GetValue() else None)


class AllocationDialog(wx.Dialog):
    """Select one approved purpose and amount for a split gift."""

    def __init__(self, parent, purposes):
        super().__init__(parent, title="Gift Allocation", size=(520, 250))
        self.purposes = purposes; panel = wx.Panel(self)
        self.purpose = wx.Choice(panel, choices=[row[1] for row in purposes])
        self.amount = wx.TextCtrl(panel); self.restriction = wx.TextCtrl(panel)
        if purposes: self.purpose.SetSelection(0)
        form = wx.FlexGridSizer(0, 2, 9, 10); form.AddGrowableCol(1, 1)
        for label, control in (("Approved purpose", self.purpose), ("Amount", self.amount),
                               ("Donor direction note", self.restriction)):
            form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); form.Add(control, 1, wx.EXPAND)
        outer = wx.BoxSizer(wx.VERTICAL); outer.Add(form, 1, wx.EXPAND | wx.ALL, 14)
        outer.Add(_dialog_buttons(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        panel.SetSizer(outer)

    def value(self):
        selected = self.purpose.GetSelection()
        if selected < 0: raise GivingValidationError("An approved purpose is required.")
        row = self.purposes[selected]
        return (row[0], row[2], row[3], row[4], self.amount.GetValue().strip(),
                self.restriction.GetValue().strip() or None), row[1]


class GiftDialog(wx.Dialog):
    """Enter a monetary gift and one or more exact allocations."""

    METHODS = ("CASH", "CHECK", "ELECTRONIC", "OTHER")
    TREATMENTS = (("Eligible", "ELIGIBLE"), ("Needs review", "REVIEW"),
                  ("Not eligible", "INELIGIBLE"))

    def __init__(self, parent, service, batch, gift=None):
        super().__init__(parent, title="Add Contribution", size=(760, 620),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = service; self.batch = batch; self.contributors = service.contributors()
        self.purposes = service.purposes(batch[3], batch[1]); self.allocations = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        form = wx.FlexGridSizer(0, 2, 8, 10); form.AddGrowableCol(1, 1)
        self.received = wx.adv.DatePickerCtrl(panel)
        self.received.SetValue(wx.DateTime.FromDMY(batch[1].day, batch[1].month - 1, batch[1].year))
        self.envelope = wx.TextCtrl(panel)
        self.contributor = wx.Choice(panel, choices=["Anonymous / resolve from envelope"] + [row[1] for row in self.contributors])
        self.contributor.SetSelection(0)
        self.method = wx.Choice(panel, choices=[item.title() for item in self.METHODS]); self.method.SetSelection(0)
        self.reference = wx.TextCtrl(panel); self.amount = wx.TextCtrl(panel)
        self.treatment = wx.Choice(panel, choices=[item[0] for item in self.TREATMENTS]); self.treatment.SetSelection(0)
        self.note = wx.TextCtrl(panel)
        for label, control in (("Received date", self.received), ("Envelope number", self.envelope),
                               ("Contributor", self.contributor), ("Method", self.method),
                               ("Check/reference", self.reference), ("Gift amount", self.amount),
                               ("Statement treatment", self.treatment), ("Note", self.note)):
            form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); form.Add(control, 1, wx.EXPAND)
        outer.Add(form, 0, wx.EXPAND | wx.ALL, 12)
        outer.Add(wx.StaticText(panel, label="Allocations must equal the gift amount exactly."), 0, wx.LEFT | wx.BOTTOM, 12)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.InsertColumn(0, "Approved purpose", width=360); self.list.InsertColumn(1, "Amount", width=120)
        self.list.InsertColumn(2, "Direction note", width=220); outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        row = wx.BoxSizer(wx.HORIZONTAL)
        add = wx.Button(panel, label="Add Allocation"); remove = wx.Button(panel, label="Remove Allocation")
        add.Bind(wx.EVT_BUTTON, self.on_add); remove.Bind(wx.EVT_BUTTON, self.on_remove)
        row.Add(add, 0, wx.RIGHT, 6); row.Add(remove); outer.Add(row, 0, wx.ALL, 12)
        outer.Add(_dialog_buttons(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer)
        self.contribution_id = None
        if gift: self.load_gift(*gift)

    def load_gift(self, header, allocations):
        """Populate the dialog from one existing draft contribution."""
        self.contribution_id = header[0]
        for index, row in enumerate(self.contributors):
            if row[0] == header[1]: self.contributor.SetSelection(index + 1); break
        self.envelope.SetValue(header[2]); self.method.SetSelection(self.METHODS.index(header[3]))
        self.reference.SetValue(header[4]); value = header[5]
        self.received.SetValue(wx.DateTime.FromDMY(value.day, value.month - 1, value.year))
        self.amount.SetValue(f"{header[6]:.2f}")
        self.treatment.SetSelection([item[1] for item in self.TREATMENTS].index(header[7]))
        self.note.SetValue(header[8]); self.allocations = [((row[0],row[1],row[2],row[3],f"{row[4]:.2f}",row[5] or ""),row[6] or "Unavailable purpose") for row in allocations]
        self.refresh()

    def on_add(self, _event=None):
        if not self.purposes:
            wx.MessageBox("Create an active approved giving purpose first.", "Gift Allocation", wx.OK | wx.ICON_INFORMATION, self); return
        dialog = AllocationDialog(self, self.purposes)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                allocation, name = dialog.value(); self.allocations.append((allocation, name)); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Add Allocation", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_remove(self, _event=None):
        selected = self.list.GetFirstSelected()
        if selected >= 0: self.allocations.pop(selected); self.refresh()

    def refresh(self):
        self.list.DeleteAllItems()
        for index, (allocation, name) in enumerate(self.allocations):
            self.list.InsertItem(index, name); self.list.SetItem(index, 1, allocation[4]); self.list.SetItem(index, 2, allocation[5] or "")

    def values(self):
        selected = self.contributor.GetSelection()
        contributor_id = self.contributors[selected - 1][0] if selected > 0 else None
        return dict(batch_id=self.batch[0], received_date=_date(self.received),
                    amount=self.amount.GetValue().strip(),
                    allocations=[item[0] for item in self.allocations], contributor_id=contributor_id,
                    envelope_number=self.envelope.GetValue(), method=self.METHODS[self.method.GetSelection()],
                    reference=self.reference.GetValue().strip() or None,
                    statement_eligibility=self.TREATMENTS[self.treatment.GetSelection()][1],
                    note=self.note.GetValue().strip() or None)


class BatchEditorDialog(wx.Dialog):
    """Show one draft batch and add confidential contribution rows."""

    def __init__(self, parent, service, batch_id, can_review=False):
        super().__init__(parent, title="Contribution Batch Entry", size=(980, 650),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = service; self.batch_id = batch_id; panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL); self.heading = wx.StaticText(panel)
        self.heading.SetFont(self.heading.GetFont().Bold().Larger()); outer.Add(self.heading, 0, wx.ALL, 12)
        self.summary = wx.StaticText(panel); outer.Add(self.summary, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Date",95),("Contributor",250),("Envelope",85),("Method",95),("Amount",110),("Statement",95))):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit)
        buttons = wx.BoxSizer(wx.HORIZONTAL); add = wx.Button(panel, label="Add Contribution")
        edit = wx.Button(panel, label="Edit Contribution"); delete = wx.Button(panel, label="Delete Contribution")
        add.Bind(wx.EVT_BUTTON, self.on_add); edit.Bind(wx.EVT_BUTTON, self.on_edit); delete.Bind(wx.EVT_BUTTON, self.on_delete)
        buttons.Add(add,0,wx.RIGHT,6); buttons.Add(edit,0,wx.RIGHT,6); buttons.Add(delete); buttons.AddStretchSpacer()
        review = wx.Button(panel, label="Review / Mark Ready")
        review.Bind(wx.EVT_BUTTON, self.on_review); review.Enable(can_review); buttons.Add(review, 0, wx.RIGHT, 8)
        close = wx.Button(panel, wx.ID_CLOSE); close.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE)); buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12); panel.SetSizer(outer); self.refresh()

    def refresh(self):
        self.batch = self.service.batch(self.batch_id)
        if not self.batch: self.EndModal(wx.ID_CLOSE); return
        self.heading.SetLabel(f"{self.batch[1]} — {self.batch[2]}")
        control = "Not entered" if self.batch[4] is None else f"${self.batch[4]:,.2f}"
        difference = (self.batch[4] - self.batch[5]) if self.batch[4] is not None else None
        text = f"Status: {self.batch[6]}    Control total: {control}    Entered: ${self.batch[5]:,.2f}"
        if difference is not None: text += f"    Difference: ${difference:,.2f}"
        self.summary.SetLabel(text); self.rows = self.service.contributions(self.batch_id); self.list.DeleteAllItems()
        for index, row in enumerate(self.rows):
            self.list.InsertItem(index, str(row[1])); self.list.SetItem(index, 1, row[2]); self.list.SetItem(index, 2, row[3])
            self.list.SetItem(index, 3, row[4].title()); self.list.SetItem(index, 4, f"${row[5]:,.2f}"); self.list.SetItem(index, 5, row[6].title())

    def on_add(self, _event=None):
        dialog = GiftDialog(self, self.service, self.batch)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.service.save_monetary_gift(**dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Save Contribution", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_edit(self, _event=None):
        selected = self.list.GetFirstSelected()
        if selected < 0: return
        gift = self.service.gift(self.batch_id, self.rows[selected][0])
        if not gift: return
        dialog = GiftDialog(self, self.service, self.batch, gift)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.service.update_monetary_gift(dialog.contribution_id, **dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Update Contribution", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_delete(self, _event=None):
        selected = self.list.GetFirstSelected()
        if selected < 0: return
        if wx.MessageBox("Delete this draft contribution?", "Delete Contribution",
                         wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES: return
        try:
            self.service.delete_gift(self.batch_id, self.rows[selected][0]); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Delete Contribution", wx.OK | wx.ICON_ERROR, self)

    def on_review(self, _event=None):
        issues = self.service.review_issues(self.batch_id)
        if issues:
            wx.MessageBox("This batch is not ready:\n\n- " + "\n- ".join(issues),
                          "Batch Review", wx.OK | wx.ICON_WARNING, self); return
        if wx.MessageBox("All review checks passed. Mark this batch Ready?",
                         "Batch Review", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self) != wx.YES:
            return
        try:
            self.service.mark_ready(self.batch_id); self.EndModal(wx.ID_OK)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Mark Batch Ready", wx.OK | wx.ICON_ERROR, self)


class BatchCatalogDialog(wx.Dialog):
    """List draft batches and open confidential batch entry."""

    def __init__(self, parent, connection, session, authorization):
        super().__init__(parent, title="Contribution Batches", size=(920, 570),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = DraftBatchService(connection, session.user_id)
        self.can_review = authorization.has_permission("giving.batches.review"); panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL); heading = wx.StaticText(panel, label="Draft Contribution Batches")
        heading.SetFont(heading.GetFont().Bold().Larger()); outer.Add(heading, 0, wx.ALL, 12)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Date",100),("Description",300),("Organization",210),("Control",100),("Entered",100))): self.list.InsertColumn(index,label,width=width)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open); outer.Add(self.list,1,wx.EXPAND|wx.LEFT|wx.RIGHT,12)
        buttons=wx.BoxSizer(wx.HORIZONTAL)
        for label,handler in (("New Batch",self.on_new),("Open Batch",self.on_open)):
            button=wx.Button(panel,label=label);button.Bind(wx.EVT_BUTTON,handler);buttons.Add(button,0,wx.RIGHT,6)
        buttons.AddStretchSpacer();close=wx.Button(panel,wx.ID_CLOSE);close.Bind(wx.EVT_BUTTON,lambda _e:self.EndModal(wx.ID_CLOSE));buttons.Add(close)
        outer.Add(buttons,0,wx.EXPAND|wx.ALL,12);panel.SetSizer(outer);self.refresh()

    def refresh(self):
        self.rows=self.service.draft_batches();self.list.DeleteAllItems()
        for index,row in enumerate(self.rows):
            self.list.InsertItem(index,str(row[1]));self.list.SetItem(index,1,row[2]);self.list.SetItem(index,2,row[3])
            self.list.SetItem(index,3,"" if row[4] is None else f"${row[4]:,.2f}");self.list.SetItem(index,4,f"${row[5]:,.2f}")

    def on_new(self,_event=None):
        dialog=NewBatchDialog(self,self.service.organizations())
        try:
            if dialog.ShowModal()==wx.ID_OK:
                batch_id=self.service.create_batch(**dialog.values());self.refresh();self._open(batch_id)
        except Exception as error:wx.MessageBox(str(error),"Unable to Create Batch",wx.OK|wx.ICON_ERROR,self)
        finally:dialog.Destroy()

    def on_open(self,_event=None):
        selected=self.list.GetFirstSelected()
        if selected>=0:self._open(self.rows[selected][0])

    def _open(self,batch_id):
        dialog=BatchEditorDialog(self,self.service,batch_id,self.can_review)
        try:dialog.ShowModal()
        finally:dialog.Destroy();self.refresh()


def show_contribution_batches(parent, connection, session, authorization):
    """Open confidential draft contribution-batch entry."""
    authorization.require("giving.batches.enter", "enter contribution batches")
    dialog = BatchCatalogDialog(parent, connection, session, authorization)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
