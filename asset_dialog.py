"""Native ChurchManager workspaces for the approved Asset subsystem."""

from __future__ import annotations
from datetime import date
from pathlib import Path
import wx
import wx.adv
from asset_repository import MariaDBAssetRepository
from asset_service import AssetService

def _choice(parent,rows,blank=True):
    control=wx.Choice(parent); control._ids=[]
    if blank: control.Append("Not assigned"); control._ids.append(None)
    for row in rows: control.Append(str(row.get("name") or "")); control._ids.append(row.get("id"))
    if control.GetCount(): control.SetSelection(0)
    return control
def _selected(control):
    index=control.GetSelection(); return control._ids[index] if 0<=index<len(control._ids) else None
def _select(control,value):
    try: control.SetSelection(control._ids.index(value))
    except ValueError: control.SetSelection(0)
def _date_value(control):
    if not control.GetValue().IsValid(): return None
    value=control.GetValue(); return date(value.GetYear(),value.GetMonth()+1,value.GetDay())
def _set_date(control,value):
    if value: control.SetValue(wx.DateTime.FromDMY(value.day,value.month-1,value.year))
def _error(parent,title,error): wx.MessageBox(str(error),title,wx.OK|wx.ICON_ERROR,parent)

class ActivityDialog(wx.Dialog):
    """Collect one immutable activity entry."""
    def __init__(self,parent,locations):
        super().__init__(parent,title="Record Asset Activity",size=(560,390)); panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL); grid=wx.FlexGridSizer(cols=2,vgap=9,hgap=12); grid.AddGrowableCol(1,1)
        self.when=wx.adv.DatePickerCtrl(panel); self.kind=wx.Choice(panel,choices=["Maintenance","Inspection","Repair","Transfer","Condition Review","Retirement","Disposal","Loss","Note"]); self.kind.SetSelection(0)
        self.summary=wx.TextCtrl(panel,style=wx.TE_MULTILINE); self.cost=wx.TextCtrl(panel); self.location=_choice(panel,locations); self.next=wx.adv.DatePickerCtrl(panel,style=wx.adv.DP_DROPDOWN|wx.adv.DP_ALLOWNONE); self.next.SetValue(wx.DateTime())
        for label,control in (("Date",self.when),("Activity",self.kind),("Summary",self.summary),("Reference cost",self.cost),("Resulting location",self.location),("Next action",self.next)):
            grid.Add(wx.StaticText(panel,label=label),0,wx.ALIGN_CENTER_VERTICAL); grid.Add(control,1,wx.EXPAND)
        outer.Add(grid,1,wx.EXPAND|wx.ALL,14); buttons=wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_OK,"Record Activity"),0,wx.RIGHT,8); buttons.Add(wx.Button(panel,wx.ID_CANCEL,"Cancel")); outer.Add(buttons,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,14); panel.SetSizer(outer)
    def values(self): return {"activity_date":_date_value(self.when),"activity_type":self.kind.GetStringSelection(),"summary":self.summary.GetValue(),"cost":self.cost.GetValue(),"location_id":_selected(self.location),"next_action":_date_value(self.next)}

class AssetEditorDialog(wx.Dialog):
    """Edit one asset and display its append-only activity history."""
    def __init__(self,parent,service,church_id,asset_id=None):
        super().__init__(parent,title="Asset",size=(920,720),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER); self.service=service; self.church_id=church_id; self.asset_id=asset_id; self.record=service.asset(asset_id) if asset_id else None; choices=service.choices(church_id)
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL); book=wx.Notebook(panel); identity=wx.Panel(book); current=wx.Panel(book); history=wx.Panel(book); book.AddPage(identity,"Identity"); book.AddPage(current,"Current Information"); book.AddPage(history,"History")
        self.number=wx.TextCtrl(identity); self.name=wx.TextCtrl(identity); self.category=wx.ComboBox(identity,choices=[r["name"] for r in choices["categories"]]); self.quantity=wx.SpinCtrl(identity,min=1,max=9999,initial=1); self.description=wx.TextCtrl(identity,style=wx.TE_MULTILINE); self.manufacturer=wx.TextCtrl(identity); self.model=wx.TextCtrl(identity); self.serial=wx.TextCtrl(identity)
        self.number.SetName("asset_number"); self.name.SetName("asset_name"); self.category.SetName("asset_category"); self.quantity.SetName("asset_quantity")
        self._layout(identity,(("Asset number",self.number),("Asset name",self.name),("Category",self.category),("Quantity",self.quantity),("Description",self.description),("Manufacturer",self.manufacturer),("Model",self.model),("Serial number",self.serial)))
        self.location=_choice(current,choices["locations"]); self.person=_choice(current,choices["people"]); self.group=_choice(current,choices["groups"]); self.condition=wx.Choice(current,choices=["Excellent","Good","Fair","Poor","Unknown"]); self.condition.SetStringSelection("Unknown"); self.status=wx.Choice(current,choices=list(AssetService.STATUSES)); self.status.SetStringSelection("Active")
        self.acquisition=wx.Choice(current,choices=["","Purchased","Donated","Transferred","Other"]); self.acquisition.SetSelection(0); self.reference=wx.TextCtrl(current); self.acquired=self._optional_date(current); self.warranty=self._optional_date(current); self.maintenance=self._optional_date(current); self.replacement=self._optional_date(current); self.retired=self._optional_date(current); self.note=wx.TextCtrl(current,style=wx.TE_MULTILINE)
        self._layout(current,(("Location",self.location),("Responsible person",self.person),("Responsible group",self.group),("Condition",self.condition),("Status",self.status),("Acquisition method",self.acquisition),("Reference value",self.reference),("Acquired",self.acquired),("Warranty expires",self.warranty),("Next maintenance",self.maintenance),("Replacement review",self.replacement),("Retired / disposed",self.retired),("Note",self.note)))
        hs=wx.BoxSizer(wx.VERTICAL); self.activity=wx.ListCtrl(history,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Date",90),("Activity",120),("Summary",350),("Cost",80),("Location",140),("Next action",90))): self.activity.InsertColumn(i,label,width=width)
        hs.Add(self.activity,1,wx.EXPAND|wx.ALL,12); self.add_activity=wx.Button(history,label="Add Activity..."); hs.Add(self.add_activity,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,12); history.SetSizer(hs); self.add_activity.Enable(bool(asset_id)); self.add_activity.Bind(wx.EVT_BUTTON,self.on_activity)
        outer.Add(book,1,wx.EXPAND|wx.ALL,10); buttons=wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer(); save=wx.Button(panel,wx.ID_OK,"Save Asset",name="asset_save"); buttons.Add(save,0,wx.RIGHT,8); buttons.Add(wx.Button(panel,wx.ID_CANCEL,"Cancel",name="asset_cancel")); outer.Add(buttons,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,10); panel.SetSizer(outer); self._fill(); self.refresh_history()
    @staticmethod
    def _optional_date(parent): control=wx.adv.DatePickerCtrl(parent,style=wx.adv.DP_DROPDOWN|wx.adv.DP_ALLOWNONE); control.SetValue(wx.DateTime()); return control
    @staticmethod
    def _layout(panel,fields):
        outer=wx.BoxSizer(wx.VERTICAL); grid=wx.FlexGridSizer(cols=2,vgap=8,hgap=12); grid.AddGrowableCol(1,1)
        for label,control in fields: grid.Add(wx.StaticText(panel,label=label),0,wx.ALIGN_CENTER_VERTICAL); grid.Add(control,1,wx.EXPAND)
        outer.Add(grid,1,wx.EXPAND|wx.ALL,14); panel.SetSizer(outer)
    def _fill(self):
        r=self.record
        if not r: return
        for control,key in ((self.number,"asset_number"),(self.name,"asset_name"),(self.category,"category"),(self.description,"description"),(self.manufacturer,"manufacturer"),(self.model,"model"),(self.serial,"serial_number"),(self.reference,"reference_value"),(self.note,"note")): control.SetValue(str(r.get(key) or ""))
        self.quantity.SetValue(r["quantity"]); _select(self.location,r.get("location_id")); _select(self.person,r.get("person_id")); _select(self.group,r.get("group_id")); self.condition.SetStringSelection(r["condition_name"]); self.status.SetStringSelection(r["status"]); self.acquisition.SetStringSelection(r.get("acquisition_method") or "")
        for control,key in ((self.acquired,"acquisition_date"),(self.warranty,"warranty_expires"),(self.maintenance,"next_maintenance"),(self.replacement,"replacement_review"),(self.retired,"retired_date")): _set_date(control,r.get(key))
    def values(self): return {"church_id":self.church_id,"asset_number":self.number.GetValue(),"asset_name":self.name.GetValue(),"category":self.category.GetValue(),"description":self.description.GetValue(),"quantity":self.quantity.GetValue(),"manufacturer":self.manufacturer.GetValue(),"model":self.model.GetValue(),"serial_number":self.serial.GetValue(),"location_id":_selected(self.location),"person_id":_selected(self.person),"group_id":_selected(self.group),"condition_name":self.condition.GetStringSelection(),"status":self.status.GetStringSelection(),"acquisition_method":self.acquisition.GetStringSelection(),"reference_value":self.reference.GetValue(),"acquisition_date":_date_value(self.acquired),"warranty_expires":_date_value(self.warranty),"next_maintenance":_date_value(self.maintenance),"replacement_review":_date_value(self.replacement),"retired_date":_date_value(self.retired),"note":self.note.GetValue()}
    def refresh_history(self):
        self.activity.DeleteAllItems(); self.activities=self.service.activities(self.asset_id) if self.asset_id else []
        for row in self.activities:
            i=self.activity.InsertItem(self.activity.GetItemCount(),str(row["activity_date"])); values=(row["activity_type"],row["summary"],str(row.get("cost") or ""),row.get("location") or "",str(row.get("next_action") or ""))
            for col,value in enumerate(values,1): self.activity.SetItem(i,col,value)
    def on_activity(self,_event):
        dialog=ActivityDialog(self,self.service.choices(self.church_id)["locations"])
        try:
            if dialog.ShowModal()==wx.ID_OK: self.service.add_activity(self.asset_id,dialog.values()); self.record=self.service.asset(self.asset_id); self.refresh_history()
        except Exception as error: _error(self,"Unable to Record Activity",error)
        finally: dialog.Destroy()

class AssetImportDialog(wx.Dialog):
    """Preview and confirm an all-or-nothing current-register CSV import."""
    def __init__(self,parent,service,church_id):
        super().__init__(parent,title="Import Assets from CSV",size=(920,620),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER); self.service=service; self.church_id=church_id; self.preview=[]; panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        help_text=wx.StaticText(panel,label="Choose a CSV file. Preview makes no database changes; every row must be Ready before import."); help_text.SetForegroundColour(wx.Colour(0,80,170)); outer.Add(help_text,0,wx.EXPAND|wx.ALL,12)
        source=wx.BoxSizer(wx.HORIZONTAL); self.path=wx.TextCtrl(panel,style=wx.TE_READONLY); browse=wx.Button(panel,label="Browse..."); source.Add(self.path,1,wx.RIGHT,8); source.Add(browse); outer.Add(source,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,12)
        self.list=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Row",55),("Asset number",120),("Asset",220),("Category",150),("Location",150),("Status",180))): self.list.InsertColumn(i,label,width=width)
        outer.Add(self.list,1,wx.EXPAND|wx.LEFT|wx.RIGHT,12); self.status=wx.StaticText(panel,label="Choose a CSV file to begin."); outer.Add(self.status,0,wx.EXPAND|wx.ALL,12)
        buttons=wx.BoxSizer(wx.HORIZONTAL); preview=wx.Button(panel,label="Preview CSV"); self.import_button=wx.Button(panel,label="Import Reviewed Rows"); self.import_button.Enable(False); buttons.Add(preview,0,wx.RIGHT,8); buttons.Add(self.import_button); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_CANCEL,"Close")); outer.Add(buttons,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,12); panel.SetSizer(outer)
        browse.Bind(wx.EVT_BUTTON,self.on_browse); preview.Bind(wx.EVT_BUTTON,self.on_preview); self.import_button.Bind(wx.EVT_BUTTON,self.on_import)
    def on_browse(self,_event):
        dialog=wx.FileDialog(self,"Choose asset CSV",wildcard="CSV files (*.csv)|*.csv",style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        try:
            if dialog.ShowModal()==wx.ID_OK:self.path.SetValue(dialog.GetPath()); self.on_preview(None)
        finally:dialog.Destroy()
    def on_preview(self,_event):
        try:
            if not self.path.GetValue():raise ValueError("Choose a CSV file first.")
            self.preview=self.service.preview_csv(self.church_id,Path(self.path.GetValue()).read_bytes()); self.list.DeleteAllItems(); blocked=0; warnings=0
            for row in self.preview:
                source=row["source"]; message="; ".join(row["errors"] or row["warnings"]) or "Ready"; blocked+=bool(row["errors"]); warnings+=bool(row["warnings"])
                i=self.list.InsertItem(self.list.GetItemCount(),str(row["line"])); values=(source["Asset Number"],source["Asset Name"],source["Category"],source["Location"],message)
                for col,value in enumerate(values,1):self.list.SetItem(i,col,value)
                if row["errors"]:self.list.SetItemTextColour(i,wx.RED)
            self.status.SetLabel(f"{len(self.preview)} row(s): {len(self.preview)-blocked} ready, {blocked} need attention, {warnings} warning(s)."); self.import_button.Enable(bool(self.preview) and not blocked)
        except Exception as error:self.import_button.Enable(False); _error(self,"Unable to Preview Asset CSV",error)
    def on_import(self,_event):
        try:
            count=self.service.import_preview(self.preview); wx.MessageBox(f"Imported {count} asset(s).","Asset Import Complete",wx.OK|wx.ICON_INFORMATION,self); self.EndModal(wx.ID_OK)
        except Exception as error:_error(self,"Unable to Import Assets",error)

class AssetsDialog(wx.Dialog):
    """Search and open the current congregational asset register."""
    def __init__(self,parent,connection,session,authorization):
        super().__init__(parent,title="Assets",size=(1000,650),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER); self.service=AssetService(MariaDBAssetRepository(connection),session,authorization); panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        title=wx.StaticText(panel,label="Congregational Assets"); font=title.GetFont(); font.MakeBold(); font.SetPointSize(font.GetPointSize()+2); title.SetFont(font); outer.Add(title,0,wx.ALL,14)
        filters=wx.BoxSizer(wx.HORIZONTAL); self.church=_choice(panel,self.service.churches(),False); self.search=wx.SearchCtrl(panel); self.status=wx.Choice(panel,choices=["All"]+list(AssetService.STATUSES)); self.status.SetSelection(0)
        for label,control in (("Church",self.church),("Find",self.search),("Status",self.status)): filters.Add(wx.StaticText(panel,label=label),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,6); filters.Add(control,1 if label!="Status" else 0,wx.RIGHT,12)
        outer.Add(filters,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,14); self.list=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Number",100),("Asset",210),("Category",130),("Location",130),("Responsible",150),("Condition",85),("Status",100),("Next maintenance",105))): self.list.InsertColumn(i,label,width=width)
        outer.Add(self.list,1,wx.EXPAND|wx.LEFT|wx.RIGHT,14); buttons=wx.BoxSizer(wx.HORIZONTAL); new=wx.Button(panel,label="New Asset..."); open_button=wx.Button(panel,label="Open Asset"); import_button=wx.Button(panel,label="Import CSV..."); export_button=wx.Button(panel,label="Export CSV..."); buttons.Add(new,0,wx.RIGHT,8); buttons.Add(open_button,0,wx.RIGHT,8); buttons.Add(import_button,0,wx.RIGHT,8); buttons.Add(export_button); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_CLOSE,"Close")); outer.Add(buttons,0,wx.EXPAND|wx.ALL,14); panel.SetSizer(outer)
        self.church.Bind(wx.EVT_CHOICE,self.refresh); self.status.Bind(wx.EVT_CHOICE,self.refresh); self.search.Bind(wx.EVT_TEXT,self.refresh); new.Bind(wx.EVT_BUTTON,self.on_new); open_button.Bind(wx.EVT_BUTTON,self.on_open); import_button.Bind(wx.EVT_BUTTON,self.on_import); export_button.Bind(wx.EVT_BUTTON,self.on_export); self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_open); self.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CLOSE),id=wx.ID_CLOSE); self.refresh()
    def refresh(self,_event=None):
        church_id=_selected(self.church); status=self.status.GetStringSelection(); self.rows=self.service.list_assets(church_id,self.search.GetValue(),"" if status=="All" else status) if church_id else []; self.list.DeleteAllItems()
        for row in self.rows:
            i=self.list.InsertItem(self.list.GetItemCount(),row["asset_number"]); vals=(row["asset_name"],row["category"],row["location"],row["responsible"],row["condition_name"],row["status"],str(row.get("next_maintenance") or ""))
            for col,value in enumerate(vals,1): self.list.SetItem(i,col,value)
    def _open(self,asset_id=None):
        dialog=AssetEditorDialog(self,self.service,_selected(self.church),asset_id)
        try:
            if dialog.ShowModal()==wx.ID_OK: self.service.save_asset(dialog.values(),asset_id); self.refresh()
        except Exception as error: _error(self,"Unable to Save Asset",error)
        finally: dialog.Destroy()
    def on_new(self,_event): self._open()
    def on_open(self,_event):
        selected=self.list.GetFirstSelected()
        if selected>=0: self._open(self.rows[selected]["id"])
    def on_import(self,_event):
        dialog=AssetImportDialog(self,self.service,_selected(self.church))
        try:
            if dialog.ShowModal()==wx.ID_OK:self.refresh()
        finally:dialog.Destroy()
    def on_export(self,_event):
        dialog=wx.FileDialog(self,"Export current asset register",wildcard="CSV files (*.csv)|*.csv",defaultFile="ChurchManager-Assets.csv",style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        try:
            if dialog.ShowModal()==wx.ID_OK:
                Path(dialog.GetPath()).write_text(self.service.export_csv(_selected(self.church)),encoding="utf-8-sig",newline="")
                wx.MessageBox("The current asset register was exported.","Asset Export Complete",wx.OK|wx.ICON_INFORMATION,self)
        except Exception as error:_error(self,"Unable to Export Assets",error)
        finally:dialog.Destroy()

class LocationsDialog(wx.Dialog):
    """Maintain reusable active asset locations."""
    def __init__(self,parent,connection,session,authorization):
        super().__init__(parent,title="Asset Locations",size=(760,540),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER); self.service=AssetService(MariaDBAssetRepository(connection),session,authorization); panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL); self.church=_choice(panel,self.service.churches(),False); outer.Add(self.church,0,wx.EXPAND|wx.ALL,12); self.list=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Location",220),("Containing location",180),("Address",240),("Active",70))): self.list.InsertColumn(i,label,width=width)
        outer.Add(self.list,1,wx.EXPAND|wx.LEFT|wx.RIGHT,12); buttons=wx.BoxSizer(wx.HORIZONTAL); add=wx.Button(panel,label="Add Location..."); buttons.Add(add); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_CLOSE,"Close")); outer.Add(buttons,0,wx.EXPAND|wx.ALL,12); panel.SetSizer(outer); self.church.Bind(wx.EVT_CHOICE,self.refresh); add.Bind(wx.EVT_BUTTON,self.on_add); self.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CLOSE),id=wx.ID_CLOSE); self.refresh()
    def refresh(self,_event=None):
        self.rows=self.service.locations(_selected(self.church)); self.list.DeleteAllItems()
        for row in self.rows:
            i=self.list.InsertItem(self.list.GetItemCount(),row["name"])
            for col,value in enumerate((row["parent"],row.get("address") or "","Yes" if row["active"] else "No"),1): self.list.SetItem(i,col,value)
    def on_add(self,_event):
        dialog=wx.TextEntryDialog(self,"Enter a clear building, room, or storage location name.","New Asset Location")
        try:
            if dialog.ShowModal()==wx.ID_OK: self.service.create_location(_selected(self.church),dialog.GetValue()); self.refresh()
        except Exception as error: _error(self,"Unable to Create Location",error)
        finally: dialog.Destroy()

class MaintenanceDialog(wx.Dialog):
    """Display a read-only due work list."""
    def __init__(self,parent,connection,session,authorization):
        super().__init__(parent,title="Asset Maintenance Due",size=(900,560),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER); self.service=AssetService(MariaDBAssetRepository(connection),session,authorization); panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL); filters=wx.BoxSizer(wx.HORIZONTAL); self.church=_choice(panel,self.service.churches(),False); self.days=wx.SpinCtrl(panel,min=0,max=365,initial=30); filters.Add(wx.StaticText(panel,label="Church"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,6); filters.Add(self.church,1,wx.RIGHT,12); filters.Add(wx.StaticText(panel,label="Due within days"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,6); filters.Add(self.days); outer.Add(filters,0,wx.EXPAND|wx.ALL,12); self.list=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Number",100),("Asset",240),("Location",180),("Maintenance",110),("Replacement review",120))): self.list.InsertColumn(i,label,width=width)
        outer.Add(self.list,1,wx.EXPAND|wx.LEFT|wx.RIGHT,12); buttons=wx.BoxSizer(wx.HORIZONTAL); open_button=wx.Button(panel,label="Open Asset"); buttons.Add(open_button); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_CLOSE,"Close")); outer.Add(buttons,0,wx.EXPAND|wx.ALL,12); panel.SetSizer(outer); self.church.Bind(wx.EVT_CHOICE,self.refresh); self.days.Bind(wx.EVT_SPINCTRL,self.refresh); open_button.Bind(wx.EVT_BUTTON,self.on_open); self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_open); self.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CLOSE),id=wx.ID_CLOSE); self.refresh()
    def refresh(self,_event=None):
        self.rows=self.service.due(_selected(self.church),self.days.GetValue()); self.list.DeleteAllItems()
        for row in self.rows:
            i=self.list.InsertItem(self.list.GetItemCount(),row["asset_number"])
            for col,value in enumerate((row["asset_name"],row["location"],str(row.get("next_maintenance") or ""),str(row.get("replacement_review") or "")),1): self.list.SetItem(i,col,value)
    def on_open(self,_event):
        selected=self.list.GetFirstSelected()
        if selected<0:return
        dialog=AssetEditorDialog(self,self.service,_selected(self.church),self.rows[selected]["id"])
        try:
            if dialog.ShowModal()==wx.ID_OK:self.service.save_asset(dialog.values(),self.rows[selected]["id"]); self.refresh()
        except Exception as error:_error(self,"Unable to Save Asset",error)
        finally:dialog.Destroy()

def _show(dialog):
    try: dialog.ShowModal()
    finally: dialog.Destroy()
def show_assets(parent,connection,session,authorization): _show(AssetsDialog(parent,connection,session,authorization))
def show_asset_locations(parent,connection,session,authorization): _show(LocationsDialog(parent,connection,session,authorization))
def show_asset_maintenance(parent,connection,session,authorization): _show(MaintenanceDialog(parent,connection,session,authorization))
