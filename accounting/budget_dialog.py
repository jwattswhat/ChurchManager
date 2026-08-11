"""Draft budget editor with account-only and detailed modes."""
import wx
from .budget_service import BudgetService
from .formatting import money

def load_choice(control,rows,optional=False):
    if optional:control.Append("(none)",None)
    for item_id,label in rows:control.Append(str(label),item_id)
    if control.GetCount():control.SetSelection(0)

class NewBudgetDialog(wx.Dialog):
    def __init__(self,parent,service):
        super().__init__(parent,title="New Draft Budget");self.service=service
        self.org=wx.Choice(self);load_choice(self.org,service.organizations());self.year=wx.Choice(self)
        self.name=wx.TextCtrl(self);self.mode=wx.Choice(self,choices=["Account Only","Detailed"]);self.mode.SetSelection(0)
        self.org.Bind(wx.EVT_CHOICE,self.refresh_years);self.refresh_years()
        grid=wx.FlexGridSizer(cols=2,hgap=8,vgap=8);grid.AddGrowableCol(1,1)
        for label,ctrl in (("Organization",self.org),("Fiscal year",self.year),("Budget name",self.name),("Reporting detail",self.mode)):
            grid.Add(wx.StaticText(self,label=label));grid.Add(ctrl,1,wx.EXPAND)
        root=wx.BoxSizer(wx.VERTICAL);root.Add(grid,1,wx.ALL|wx.EXPAND,12);root.Add(self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL),0,wx.ALL|wx.EXPAND,10);self.SetSizerAndFit(root);self.SetMinSize((520,self.GetSize().height))
    def refresh_years(self,event=None):
        self.year.Clear();i=self.org.GetSelection()
        if i!=wx.NOT_FOUND:load_choice(self.year,self.service.years(self.org.GetClientData(i)))
    def values(self):
        if self.org.GetSelection()==wx.NOT_FOUND or self.year.GetSelection()==wx.NOT_FOUND:raise ValueError("Select an organization and fiscal year.")
        return self.org.GetClientData(self.org.GetSelection()),self.year.GetClientData(self.year.GetSelection()),self.name.GetValue(),("ACCOUNT_ONLY" if self.mode.GetSelection()==0 else "DETAILED")

class BudgetLineDialog(wx.Dialog):
    def __init__(self,parent,context,initial=None):
        super().__init__(parent,title="Budget Line");self.detailed=context["header"][3]=="DETAILED"
        self.period=wx.Choice(self);self.account=wx.Choice(self);self.fund=wx.Choice(self);self.function=wx.Choice(self)
        load_choice(self.period,context["periods"]);load_choice(self.account,context["accounts"]);load_choice(self.fund,context["funds"]);load_choice(self.function,context["functions"],True)
        self.item=wx.TextCtrl(self);self.item.Enable(self.detailed);self.amount=wx.TextCtrl(self);self.note=wx.TextCtrl(self)
        grid=wx.FlexGridSizer(cols=2,hgap=8,vgap=8);grid.AddGrowableCol(1,1)
        for label,ctrl in (("Fiscal period",self.period),("General account",self.account),("Fund",self.fund),("Function",self.function),("Detailed line item",self.item),("Amount",self.amount),("Note",self.note)):
            grid.Add(wx.StaticText(self,label=label));grid.Add(ctrl,1,wx.EXPAND)
        root=wx.BoxSizer(wx.VERTICAL);root.Add(grid,1,wx.ALL|wx.EXPAND,12);root.Add(self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL),0,wx.ALL|wx.EXPAND,10);self.SetSizerAndFit(root);self.SetMinSize((600,self.GetSize().height))
        if initial:
            for ctrl,value in ((self.period,initial[8]),(self.account,initial[9]),(self.fund,initial[10]),(self.function,initial[11])):
                for i in range(ctrl.GetCount()):
                    if ctrl.GetClientData(i)==value:ctrl.SetSelection(i);break
            self.item.SetValue(initial[5] or "");self.amount.SetValue(str(initial[6]));self.note.SetValue(initial[7] or "")
    def values(self):
        for ctrl,label in ((self.period,"period"),(self.account,"account"),(self.fund,"fund")):
            if ctrl.GetSelection()==wx.NOT_FOUND:raise ValueError("Select a {}.".format(label))
        fi=self.function.GetSelection()
        return {"period_id":self.period.GetClientData(self.period.GetSelection()),"account_id":self.account.GetClientData(self.account.GetSelection()),"fund_id":self.fund.GetClientData(self.fund.GetSelection()),"function_id":None if fi==wx.NOT_FOUND else self.function.GetClientData(fi),"line_item":self.item.GetValue(),"amount":self.amount.GetValue(),"note":self.note.GetValue()}

class BudgetDialog(wx.Dialog):
    def __init__(self,parent,service,can_adopt=False,can_override=False):
        super().__init__(parent,title="Accounting Budgets",size=(1050,650));self.service=service;self.rows=[];self.line_rows=[];self.current=None
        self.budgets=wx.ListCtrl(self,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Organization",170),("Year",90),("Budget",190),("Version",65),("Mode",110),("Status",90))):self.budgets.InsertColumn(i,label,width=width)
        self.lines=wx.ListCtrl(self,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Period",90),("General account",190),("Fund",140),("Function",110),("Detailed line item",180),("Amount",95),("Note",160))):self.lines.InsertColumn(i,label,width=width)
        col=self.lines.GetColumn(5);col.SetAlign(wx.LIST_FORMAT_RIGHT);self.lines.SetColumn(5,col)
        self.budgets.Bind(wx.EVT_LIST_ITEM_SELECTED,self.on_budget);self.lines.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_edit)
        self.can_adopt=can_adopt;self.can_override=can_override
        new=wx.Button(self,label="New Budget");add=wx.Button(self,label="Add Line");edit=wx.Button(self,label="Edit Line");propose=wx.Button(self,label="Propose");adopt=wx.Button(self,label="Adopt");solo=wx.Button(self,label="Solo Adopt");close=wx.Button(self,wx.ID_CLOSE,"Close")
        new.Bind(wx.EVT_BUTTON,self.on_new);add.Bind(wx.EVT_BUTTON,self.on_add);edit.Bind(wx.EVT_BUTTON,self.on_edit);propose.Bind(wx.EVT_BUTTON,self.on_propose);adopt.Bind(wx.EVT_BUTTON,self.on_adopt);solo.Bind(wx.EVT_BUTTON,self.on_solo_adopt);close.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CLOSE));adopt.Enable(can_adopt);solo.Enable(can_adopt and can_override)
        buttons=wx.BoxSizer(wx.HORIZONTAL);buttons.Add(new);buttons.Add(add,0,wx.LEFT,8);buttons.Add(edit,0,wx.LEFT,8);buttons.Add(propose,0,wx.LEFT,8);buttons.AddStretchSpacer();buttons.Add(adopt,0,wx.RIGHT,8);buttons.Add(solo,0,wx.RIGHT,8);buttons.Add(close)
        root=wx.BoxSizer(wx.VERTICAL);root.Add(self.budgets,1,wx.ALL|wx.EXPAND,10);root.Add(self.lines,2,wx.LEFT|wx.RIGHT|wx.EXPAND,10);root.Add(buttons,0,wx.ALL|wx.EXPAND,10);self.SetSizer(root);self.refresh()
    def refresh(self):
        self.rows=self.service.budgets();self.budgets.DeleteAllItems();self.lines.DeleteAllItems();self.current=None
        for item in self.rows:
            row=self.budgets.InsertItem(self.budgets.GetItemCount(),str(item[1]));vals=(item[2],item[3],item[4],"Account Only" if item[5]=="ACCOUNT_ONLY" else "Detailed",item[6])
            for c,v in enumerate(vals,1):self.budgets.SetItem(row,c,str(v))
    def on_budget(self,event):
        self.current=self.rows[event.GetIndex()][0];self.reload_lines()
    def reload_lines(self):
        self.line_rows=self.service.lines(self.current);self.lines.DeleteAllItems()
        for item in self.line_rows:
            row=self.lines.InsertItem(self.lines.GetItemCount(),str(item[1]));vals=(*item[2:6],money(item[6]),item[7] or "")
            for c,v in enumerate(vals,1):self.lines.SetItem(row,c,str(v))
    def on_new(self,event):
        d=NewBudgetDialog(self,self.service)
        try:
            if d.ShowModal()!=wx.ID_OK:return
            self.service.create(*d.values());self.refresh()
        except ValueError as e:wx.MessageBox(str(e),"Budget not created",wx.OK|wx.ICON_WARNING)
        finally:d.Destroy()
    def edit_line(self,initial=None):
        if self.current is None:wx.MessageBox("Select a budget first.","Budgets");return
        d=BudgetLineDialog(self,self.service.context(self.current),initial)
        try:
            if d.ShowModal()!=wx.ID_OK:return
            self.service.save_line(self.current,d.values(),None if initial is None else initial[0]);self.reload_lines()
        except ValueError as e:wx.MessageBox(str(e),"Budget line not saved",wx.OK|wx.ICON_WARNING)
        finally:d.Destroy()
    def on_add(self,event):self.edit_line()
    def on_edit(self,event):
        i=event.GetIndex() if hasattr(event,"GetIndex") else self.lines.GetFirstSelected()
        if i>=0:self.edit_line(self.line_rows[i])
    def on_propose(self,event):
        if self.current is None:return
        try:self.service.propose(self.current);self.refresh()
        except ValueError as e:wx.MessageBox(str(e),"Budget not proposed",wx.OK|wx.ICON_WARNING)
    def on_adopt(self,event):
        if self.current is None:return
        try:self.service.adopt(self.current);self.refresh()
        except ValueError as e:wx.MessageBox(str(e),"Budget not adopted",wx.OK|wx.ICON_WARNING)
    def on_solo_adopt(self,event):
        if self.current is None:return
        d=wx.TextEntryDialog(self,"Explain why independent adoption is unavailable.","Solo Budget Adoption")
        try:
            if d.ShowModal()!=wx.ID_OK:return
            self.service.adopt(self.current,d.GetValue(),True);self.refresh()
        except ValueError as e:wx.MessageBox(str(e),"Budget not adopted",wx.OK|wx.ICON_WARNING)
        finally:d.Destroy()

def show_budgets(parent,connection,session,authorization):
    authorization.require("accounting.budgets.manage","manage accounting budgets")
    d=BudgetDialog(parent,BudgetService(connection,session.user_id),authorization.has_permission("accounting.budgets.adopt"),authorization.has_permission("accounting.approval.override"))
    try:d.ShowModal()
    finally:d.Destroy()
