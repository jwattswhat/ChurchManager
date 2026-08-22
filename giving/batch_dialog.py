"""Confidential contribution-batch entry and accounting handoff dialogs."""

from datetime import date

import wx
import wx.adv

from giving.batch_service import DraftBatchService
from giving.accounting_handoff import GivingAccountingHandoff
from giving.correction_service import PostedBatchCorrectionService
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

    def __init__(self, parent, service, organizations, batch=None):
        super().__init__(parent, title=("Edit Contribution Batch" if batch else "New Contribution Batch"),
                         size=(620, 390))
        self.service = service; self.organizations = organizations; self.bank_accounts = []
        panel = wx.Panel(self); form = wx.FlexGridSizer(0, 2, 9, 10); form.AddGrowableCol(1, 1)
        self.batch_date = wx.adv.DatePickerCtrl(panel)
        self.description = wx.TextCtrl(panel)
        self.organization = wx.Choice(panel, choices=[row[1] for row in organizations])
        self.bank_account = wx.Choice(panel)
        self.control = wx.TextCtrl(panel)
        self.deposit = wx.adv.DatePickerCtrl(panel)
        self.has_deposit = wx.CheckBox(panel, label="Deposit date is known")
        self.open_periods = wx.StaticText(panel)
        for label, control in (("Batch date", self.batch_date), ("Description", self.description),
                               ("Accounting organization", self.organization),
                               ("Deposit bank account", self.bank_account),
                               ("Expected/control total", self.control), ("", self.has_deposit),
                               ("Deposit date", self.deposit), ("Open fiscal periods", self.open_periods)):
            form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            form.Add(control, 1, wx.EXPAND)
        self.organization.SetSelection(0 if organizations else wx.NOT_FOUND)
        self.organization.Bind(wx.EVT_CHOICE, self.on_organization); self.on_organization()
        self.has_deposit.SetValue(True)
        self.has_deposit.Bind(wx.EVT_CHECKBOX, lambda _e: self.deposit.Enable(self.has_deposit.GetValue()))
        buttons = _dialog_buttons(panel)
        outer = wx.BoxSizer(wx.VERTICAL); outer.Add(form, 1, wx.EXPAND | wx.ALL, 14)
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)
        if batch:
            self._load_batch(batch)

    def on_organization(self, _event=None):
        """Refresh eligible deposit accounts for the selected organization."""
        selected = self.organization.GetSelection()
        self.bank_accounts = (
            self.service.bank_accounts(self.organizations[selected][0])
            if selected >= 0 else []
        )
        self.bank_account.Set([row[1] for row in self.bank_accounts])
        self.bank_account.SetSelection(0 if self.bank_accounts else wx.NOT_FOUND)
        periods = self.service.open_fiscal_periods(
            self.organizations[selected][0]) if selected >= 0 else []
        if periods:
            first, last = periods[0], periods[-1]
            text = f"{first[1]:%m/%d/%Y} through {last[2]:%m/%d/%Y}"
        else:
            text = "None"
        self.open_periods.SetLabel(text)

    def _load_batch(self, batch):
        """Populate a Draft header and keep its accounting organization fixed."""
        self.batch_date.SetValue(wx.DateTime.FromDMY(batch[1].day, batch[1].month - 1, batch[1].year))
        self.description.SetValue(batch[2]); self.organization.SetSelection(next(
            (index for index, row in enumerate(self.organizations) if row[0] == batch[3]), wx.NOT_FOUND))
        self.organization.Enable(False); self.on_organization()
        bank_index = next((index for index, row in enumerate(self.bank_accounts) if row[0] == batch[9]), wx.NOT_FOUND)
        self.bank_account.SetSelection(bank_index)
        self.control.SetValue("" if batch[4] is None else f"{batch[4]:.2f}")
        self.has_deposit.SetValue(batch[8] is not None); self.deposit.Enable(batch[8] is not None)
        if batch[8] is not None:
            self.deposit.SetValue(wx.DateTime.FromDMY(batch[8].day, batch[8].month - 1, batch[8].year))

    def values(self):
        selected = self.organization.GetSelection()
        if selected < 0:
            raise GivingValidationError("An accounting organization is required.")
        bank = self.bank_account.GetSelection()
        if bank < 0:
            raise GivingValidationError("An active deposit bank account is required.")
        return dict(batch_date=_date(self.batch_date), description=self.description.GetValue(),
                    organization_id=self.organizations[selected][0],
                    bank_account_id=self.bank_accounts[bank][0],
                    control_total=self.control.GetValue().strip() or None,
                    deposit_date=_date(self.deposit) if self.has_deposit.GetValue() else None)


class AllocationDialog(wx.Dialog):
    """Select one approved purpose and amount for a split gift."""

    def __init__(self, parent, purposes, non_cash=False):
        super().__init__(parent, title="Gift Allocation", size=(520, 250))
        self.purposes = purposes; panel = wx.Panel(self)
        self.purpose = wx.Choice(panel, choices=[row[1] for row in purposes])
        self.amount = wx.TextCtrl(panel); self.restriction = wx.TextCtrl(panel)
        if non_cash:
            self.amount.SetValue("0.00")
            self.amount.Enable(False)
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
        return (row[0], row[2], row[3], row[4], row[5], self.amount.GetValue().strip(),
                self.restriction.GetValue().strip() or None), row[1]


class GiftDialog(wx.Dialog):
    """Enter a monetary gift or a description-only non-cash contribution."""

    METHODS = ("CASH", "CHECK", "ELECTRONIC", "NON_CASH", "OTHER")
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
        self.non_cash_description = wx.TextCtrl(panel)
        self.donor_estimated_value = wx.TextCtrl(panel)
        self.treatment = wx.Choice(panel, choices=[item[0] for item in self.TREATMENTS]); self.treatment.SetSelection(0)
        self.note = wx.TextCtrl(panel)
        self.facts = {
            "goods_or_services_provided": False,
            "goods_or_services_description": None,
            "goods_or_services_value": None,
            "intangible_religious_benefit_only": False,
            "tribute_type": None,
            "honoree_name": None,
            "acknowledgment_contact": None,
            "donor_disclosure_authorized": False,
            "amount_disclosure_authorized": False,
            "eligibility_override_reason": None,
        }
        for label, control in (("Received date", self.received), ("Envelope number", self.envelope),
                               ("Contributor", self.contributor), ("Method", self.method),
                               ("Check/reference", self.reference), ("Gift amount", self.amount),
                               ("Donated property", self.non_cash_description),
                               ("Donor-provided estimate (unverified)", self.donor_estimated_value),
                               ("Statement treatment", self.treatment), ("Note", self.note)):
            form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); form.Add(control, 1, wx.EXPAND)
        outer.Add(form, 0, wx.EXPAND | wx.ALL, 12)
        facts_row = wx.BoxSizer(wx.HORIZONTAL)
        facts_button = wx.Button(panel, label="Acknowledgment / Tribute...")
        facts_button.Bind(wx.EVT_BUTTON, self.on_facts)
        self.facts_summary = wx.StaticText(panel, label="No special acknowledgment facts")
        facts_row.Add(facts_button, 0, wx.RIGHT, 10)
        facts_row.Add(self.facts_summary, 1, wx.ALIGN_CENTER_VERTICAL)
        outer.Add(facts_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
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
        self.method.Bind(wx.EVT_CHOICE, self.on_method)
        self.contribution_id = None
        if gift:
            self.load_gift(*gift)
        else:
            self.on_method()

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
        self.note.SetValue(header[8])
        self.facts.update({
            "goods_or_services_provided": bool(header[9]),
            "goods_or_services_description": header[10] or None,
            "goods_or_services_value": None if header[11] is None else f"{header[11]:.2f}",
            "intangible_religious_benefit_only": bool(header[12]),
            "tribute_type": header[13], "honoree_name": header[14] or None,
            "acknowledgment_contact": header[15] or None,
            "donor_disclosure_authorized": bool(header[16]),
            "amount_disclosure_authorized": bool(header[17]),
            "eligibility_override_reason": header[18] or None,
        })
        self.non_cash_description.SetValue(header[19] or "")
        self.donor_estimated_value.SetValue("" if header[20] is None else f"{header[20]:.2f}")
        self.allocations = [((row[0],row[1],row[2],row[3],row[4],f"{row[5]:.2f}",row[6] or ""),row[7] or "Unavailable purpose") for row in allocations]
        self.on_method()
        self.refresh()

    def on_method(self, _event=None):
        """Switch between valued gifts and description-only donated property."""
        non_cash = self.METHODS[self.method.GetSelection()] == "NON_CASH"
        if non_cash:
            self.amount.SetValue("0.00")
        self.amount.Enable(not non_cash)
        self.non_cash_description.Enable(non_cash)
        self.donor_estimated_value.Enable(non_cash)
        if not non_cash:
            self.non_cash_description.SetValue("")
            self.donor_estimated_value.SetValue("")

    def on_facts(self, _event=None):
        dialog = GiftFactsDialog(self, self.facts)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.facts = dialog.values()
                self.refresh_facts_summary()
        finally:
            dialog.Destroy()

    def refresh_facts_summary(self):
        labels = []
        if self.facts["goods_or_services_provided"]:
            labels.append("goods/services provided")
        elif self.facts["intangible_religious_benefit_only"]:
            labels.append("intangible religious benefit")
        if self.facts["tribute_type"]:
            labels.append("memorial/honor gift")
        if self.facts["eligibility_override_reason"]:
            labels.append("statement review noted")
        self.facts_summary.SetLabel(", ".join(labels).capitalize() if labels else "No special acknowledgment facts")

    def on_add(self, _event=None):
        if not self.purposes:
            wx.MessageBox("Create an active approved giving purpose first.", "Gift Allocation", wx.OK | wx.ICON_INFORMATION, self); return
        non_cash = self.METHODS[self.method.GetSelection()] == "NON_CASH"
        dialog = AllocationDialog(self, self.purposes, non_cash=non_cash)
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
            self.list.InsertItem(index, name); self.list.SetItem(index, 1, allocation[5]); self.list.SetItem(index, 2, allocation[6] or "")

    def values(self):
        selected = self.contributor.GetSelection()
        contributor_id = self.contributors[selected - 1][0] if selected > 0 else None
        values = dict(batch_id=self.batch[0], received_date=_date(self.received),
                    amount=self.amount.GetValue().strip(),
                    allocations=[item[0] for item in self.allocations], contributor_id=contributor_id,
                    envelope_number=self.envelope.GetValue(), method=self.METHODS[self.method.GetSelection()],
                    reference=self.reference.GetValue().strip() or None,
                    statement_eligibility=self.TREATMENTS[self.treatment.GetSelection()][1],
                    non_cash_description=self.non_cash_description.GetValue().strip() or None,
                    donor_estimated_value=self.donor_estimated_value.GetValue().strip() or None,
                    note=self.note.GetValue().strip() or None)
        values.update(self.facts)
        return values


class GiftFactsDialog(wx.Dialog):
    """Collect restricted acknowledgment and memorial facts for one gift."""

    TRIBUTES = (("Not a memorial or honor gift", None),
                ("In memory of", "IN_MEMORY_OF"), ("In honor of", "IN_HONOR_OF"))

    def __init__(self, parent, values):
        super().__init__(parent, title="Acknowledgment and Tribute Facts", size=(680, 570),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        notice = wx.StaticText(panel, label=(
            "Record congregation-determined facts only. ChurchManager does not decide tax deductibility."
        ))
        notice.SetForegroundColour(wx.Colour(0, 82, 170)); outer.Add(notice, 0, wx.ALL, 12)

        benefit_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Goods or services")
        self.goods = wx.CheckBox(panel, label="Goods or services were provided")
        self.intangible = wx.CheckBox(panel, label="Only intangible religious benefits were provided")
        self.goods_description = wx.TextCtrl(panel)
        self.goods_value = wx.TextCtrl(panel)
        benefit_form = wx.FlexGridSizer(0, 2, 8, 10); benefit_form.AddGrowableCol(1, 1)
        benefit_form.Add(wx.StaticText(panel, label="Description"), 0, wx.ALIGN_CENTER_VERTICAL)
        benefit_form.Add(self.goods_description, 1, wx.EXPAND)
        benefit_form.Add(wx.StaticText(panel, label="Good-faith value"), 0, wx.ALIGN_CENTER_VERTICAL)
        benefit_form.Add(self.goods_value, 1, wx.EXPAND)
        benefit_box.Add(self.goods, 0, wx.ALL, 8); benefit_box.Add(self.intangible, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        benefit_box.Add(benefit_form, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        outer.Add(benefit_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        tribute_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Memorial or honor gift")
        tribute_form = wx.FlexGridSizer(0, 2, 8, 10); tribute_form.AddGrowableCol(1, 1)
        self.tribute = wx.Choice(panel, choices=[item[0] for item in self.TRIBUTES]); self.tribute.SetSelection(0)
        self.honoree = wx.TextCtrl(panel); self.contact = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        for label, control in (("Type", self.tribute), ("Person remembered or honored", self.honoree),
                               ("Acknowledgment contact", self.contact)):
            tribute_form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            tribute_form.Add(control, 1, wx.EXPAND)
        self.disclose_donor = wx.CheckBox(panel, label="Contributor explicitly authorized disclosure of donor identity")
        self.disclose_amount = wx.CheckBox(panel, label="Contributor explicitly authorized disclosure of gift amount")
        tribute_box.Add(tribute_form, 1, wx.EXPAND | wx.ALL, 8)
        tribute_box.Add(self.disclose_donor, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        tribute_box.Add(self.disclose_amount, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        outer.Add(tribute_box, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        review = wx.BoxSizer(wx.HORIZONTAL)
        review.Add(wx.StaticText(panel, label="Statement-treatment review reason"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        self.override_reason = wx.TextCtrl(panel); review.Add(self.override_reason, 1, wx.EXPAND)
        outer.Add(review, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        outer.Add(_dialog_buttons(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer)

        self.goods.SetValue(bool(values.get("goods_or_services_provided")))
        self.goods_description.SetValue(values.get("goods_or_services_description") or "")
        self.goods_value.SetValue(values.get("goods_or_services_value") or "")
        self.intangible.SetValue(bool(values.get("intangible_religious_benefit_only")))
        tribute_type = values.get("tribute_type")
        self.tribute.SetSelection(next((i for i, item in enumerate(self.TRIBUTES) if item[1] == tribute_type), 0))
        self.honoree.SetValue(values.get("honoree_name") or "")
        self.contact.SetValue(values.get("acknowledgment_contact") or "")
        self.disclose_donor.SetValue(bool(values.get("donor_disclosure_authorized")))
        self.disclose_amount.SetValue(bool(values.get("amount_disclosure_authorized")))
        self.override_reason.SetValue(values.get("eligibility_override_reason") or "")

    def values(self):
        return {
            "goods_or_services_provided": self.goods.GetValue(),
            "goods_or_services_description": self.goods_description.GetValue().strip() or None,
            "goods_or_services_value": self.goods_value.GetValue().strip() or None,
            "intangible_religious_benefit_only": self.intangible.GetValue(),
            "tribute_type": self.TRIBUTES[self.tribute.GetSelection()][1],
            "honoree_name": self.honoree.GetValue().strip() or None,
            "acknowledgment_contact": self.contact.GetValue().strip() or None,
            "donor_disclosure_authorized": self.disclose_donor.GetValue(),
            "amount_disclosure_authorized": self.disclose_amount.GetValue(),
            "eligibility_override_reason": self.override_reason.GetValue().strip() or None,
        }


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
        details = wx.Button(panel, label="Edit Batch Details")
        details.Bind(wx.EVT_BUTTON, self.on_details)
        buttons.Add(details,0,wx.RIGHT,6); buttons.Add(add,0,wx.RIGHT,6); buttons.Add(edit,0,wx.RIGHT,6); buttons.Add(delete); buttons.AddStretchSpacer()
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
            self.list.SetItem(index, 3, row[4].replace("_", " ").title())
            amount = "Non-cash" if row[4] == "NON_CASH" else f"${row[5]:,.2f}"
            self.list.SetItem(index, 4, amount); self.list.SetItem(index, 5, row[6].title())

    def on_add(self, _event=None):
        dialog = GiftDialog(self, self.service, self.batch)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.service.save_monetary_gift(**dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Save Contribution", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_details(self, _event=None):
        dialog = NewBatchDialog(self, self.service, self.service.organizations(), self.batch)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.service.update_batch_header(self.batch_id, **dialog.values()); self.refresh()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Update Batch", wx.OK | wx.ICON_ERROR, self)
        finally:
            dialog.Destroy()

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
        if wx.MessageBox("All review checks passed. Complete this batch review?",
                         "Batch Review", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self) != wx.YES:
            return
        try:
            status = self.service.mark_ready(self.batch_id)
            if status == "POSTED":
                wx.MessageBox(
                    "The non-cash batch is complete. No accounting transaction was created.",
                    "Non-cash Contributions", wx.OK | wx.ICON_INFORMATION, self,
                )
            self.EndModal(wx.ID_OK)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Mark Batch Ready", wx.OK | wx.ICON_ERROR, self)


class BatchCatalogDialog(wx.Dialog):
    """List Giving batches that still require entry or accounting handoff."""

    def __init__(self, parent, connection, session, authorization, test_mode=False):
        super().__init__(parent, title="Contribution Batches", size=(920, 570),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = DraftBatchService(connection, session.user_id, authorization)
        self.authorization = authorization
        self.test_mode = bool(test_mode)
        self.can_review = authorization.has_permission("giving.batches.review")
        self.can_post = authorization.has_permission("giving.batches.post"); panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL); heading = wx.StaticText(panel, label="Contribution Batches")
        heading.SetFont(heading.GetFont().Bold().Larger()); outer.Add(heading, 0, wx.ALL, 12)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Date",100),("Description",260),("Organization",190),("Status",80),("Control",100),("Entered",100))): self.list.InsertColumn(index,label,width=width)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open); outer.Add(self.list,1,wx.EXPAND|wx.LEFT|wx.RIGHT,12)
        buttons=wx.BoxSizer(wx.HORIZONTAL)
        for label,handler in (("New Batch",self.on_new),("Open Batch",self.on_open)):
            button=wx.Button(panel,label=label);button.Bind(wx.EVT_BUTTON,handler);buttons.Add(button,0,wx.RIGHT,6)
        import_csv=wx.Button(panel,label="Import CSV...")
        import_csv.Bind(wx.EVT_BUTTON,self.on_import);buttons.Add(import_csv,0,wx.RIGHT,6)
        send=wx.Button(panel,label="Send Ready Batch to Accounting")
        send.Bind(wx.EVT_BUTTON,self.on_send);send.Enable(self.can_post);buttons.Add(send,0,wx.RIGHT,6)
        return_draft=wx.Button(panel,label="Return Ready to Draft")
        return_draft.Bind(wx.EVT_BUTTON,self.on_return_to_draft)
        return_draft.Enable(self.can_review);buttons.Add(return_draft,0,wx.RIGHT,6)
        correct=wx.Button(panel,label="Correct Posted Batch...")
        correct.Bind(wx.EVT_BUTTON,self.on_correct);correct.Enable(self.can_post);buttons.Add(correct,0,wx.RIGHT,6)
        buttons.AddStretchSpacer();close=wx.Button(panel,wx.ID_CLOSE);close.Bind(wx.EVT_BUTTON,lambda _e:self.EndModal(wx.ID_CLOSE));buttons.Add(close)
        outer.Add(buttons,0,wx.EXPAND|wx.ALL,12);panel.SetSizer(outer);self.refresh()

    def refresh(self):
        self.rows=self.service.catalog_batches();self.list.DeleteAllItems()
        for index,row in enumerate(self.rows):
            self.list.InsertItem(index,str(row[1]));self.list.SetItem(index,1,row[2]);self.list.SetItem(index,2,row[3])
            display_status = "Sent to Accounting" if row[7] == "READY" and row[8] is not None else row[7].title()
            self.list.SetItem(index,3,display_status);self.list.SetItem(index,4,"" if row[4] is None else f"${row[4]:,.2f}");self.list.SetItem(index,5,f"${row[5]:,.2f}")

    def on_new(self,_event=None):
        dialog=NewBatchDialog(self,self.service,self.service.organizations())
        try:
            if dialog.ShowModal()==wx.ID_OK:
                batch_id=self.service.create_batch(**dialog.values());self.refresh();self._open(batch_id)
        except Exception as error:wx.MessageBox(str(error),"Unable to Create Batch",wx.OK|wx.ICON_ERROR,self)
        finally:dialog.Destroy()

    def on_import(self, _event=None):
        from giving.import_dialog import show_contribution_import_preview
        batch_id = show_contribution_import_preview(self, self.service, self.test_mode)
        if batch_id is not None: self.refresh(); self._open(batch_id)

    def on_open(self,_event=None):
        selected=self.list.GetFirstSelected()
        if selected>=0 and self.rows[selected][7]=="DRAFT":self._open(self.rows[selected][0])

    def on_send(self,_event=None):
        selected=self.list.GetFirstSelected()
        if selected<0:return
        row=self.rows[selected]
        if row[7]!="READY":
            wx.MessageBox("Select a Ready contribution batch.","Accounting Handoff",wx.OK|wx.ICON_INFORMATION,self);return
        if row[8] is not None:
            wx.MessageBox("That batch is already waiting in Accounting Review or Transaction Posting.",
                          "Accounting Handoff",wx.OK|wx.ICON_INFORMATION,self);return
        if wx.MessageBox("Create one summarized accounting transaction for this batch?\n\nNo donor or envelope details will enter the ledger.",
                         "Send to Accounting",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION,self)!=wx.YES:return
        try:
            transaction_id=GivingAccountingHandoff(
                self.service.connection, self.service.user_id, self.authorization
            ).send(row[0])
            wx.MessageBox(f"Accounting transaction {transaction_id} is Ready in Transaction Posting.",
                          "Accounting Handoff",wx.OK|wx.ICON_INFORMATION,self);self.refresh()
        except Exception as error:wx.MessageBox(str(error),"Unable to Send Batch",wx.OK|wx.ICON_ERROR,self)

    def on_return_to_draft(self, _event=None):
        selected = self.list.GetFirstSelected()
        if selected < 0 or self.rows[selected][7] != "READY" or self.rows[selected][8] is not None:
            wx.MessageBox("Select an unsent Ready contribution batch.", "Return Batch to Draft",
                          wx.OK | wx.ICON_INFORMATION, self); return
        if wx.MessageBox(
                "Return this Ready batch to Draft so it can be corrected?",
                "Return Batch to Draft", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self) != wx.YES:
            return
        try:
            batch_id = self.rows[selected][0]
            self.service.return_to_draft(batch_id); self.refresh(); self._open(batch_id)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Return Batch", wx.OK | wx.ICON_ERROR, self)

    def on_correct(self, _event=None):
        selected = self.list.GetFirstSelected()
        if selected < 0 or self.rows[selected][7] != "POSTED":
            wx.MessageBox("Select a Posted contribution batch.", "Correct Posted Batch",
                          wx.OK | wx.ICON_INFORMATION, self); return
        dialog = PostedBatchCorrectionDialog(self)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            if wx.MessageBox(
                    "Create an accounting reversal and an editable replacement batch?\n\n"
                    "The reversal must be approved and posted before the replacement can be sent to accounting.",
                    "Correct Posted Batch", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES: return
            replacement, reversal = PostedBatchCorrectionService(
                self.service.connection, self.service.user_id, self.authorization).create(
                    self.rows[selected][0], dialog.correction_date(), dialog.reason.GetValue())
            wx.MessageBox(
                f"Replacement batch {replacement} was created. Accounting reversal {reversal} is Ready.",
                "Correction Created", wx.OK | wx.ICON_INFORMATION, self)
            self.refresh(); self._open(replacement)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Correct Posted Batch", wx.OK | wx.ICON_ERROR, self)
        finally:
            dialog.Destroy()

    def _open(self,batch_id):
        dialog=BatchEditorDialog(self,self.service,batch_id,self.can_review)
        try:dialog.ShowModal()
        finally:dialog.Destroy();self.refresh()


class PostedBatchCorrectionDialog(wx.Dialog):
    """Collect the open-period correction date and required audit reason."""

    def __init__(self, parent):
        super().__init__(parent, title="Correct Posted Contribution Batch")
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(wx.StaticText(panel, label="Correction date"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)
        self.date = wx.adv.DatePickerCtrl(panel); outer.Add(self.date, 0, wx.EXPAND | wx.ALL, 12)
        outer.Add(wx.StaticText(panel, label="Reason for correction"), 0, wx.LEFT | wx.RIGHT, 12)
        self.reason = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(460, 100))
        outer.Add(self.reason, 1, wx.EXPAND | wx.ALL, 12)
        outer.Add(_dialog_buttons(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(outer); outer.Fit(self)

    def correction_date(self):
        """Return the selected correction date as a Python date."""
        return _date(self.date)


def show_contribution_batches(parent, connection, session, authorization, test_mode=False):
    """Open confidential contribution-batch entry and accounting handoff."""
    authorization.require("giving.batches.enter", "enter contribution batches")
    dialog = BatchCatalogDialog(parent, connection, session, authorization, test_mode)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
