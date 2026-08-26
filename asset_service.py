"""Authorization and validation boundary for congregational assets."""

from __future__ import annotations
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from asset_exchange import read_csv, write_csv


class AssetValidationError(ValueError):
    """Raised when asset data violates the approved contract."""


class AssetService:
    """Validate and authorize all user-facing asset operations."""

    STATUSES=("Active","In Storage","Loaned","Under Repair","Retired","Lost","Disposed")
    RETIRED={"Retired","Lost","Disposed"}

    def __init__(self,repository,session,authorization): self.repository=repository; self.session=session; self.authorization=authorization
    def churches(self): self.authorization.require("assets.view","view assets"); return self.repository.churches()
    def choices(self,church_id): self.authorization.require("assets.view","view asset choices"); return self.repository.choices(_id(church_id,"church"))
    def list_assets(self,church_id,search="",status=""): self.authorization.require("assets.view","view assets"); return self.repository.list_assets(_id(church_id,"church"),search,status)
    def asset(self,asset_id): self.authorization.require("assets.view","view an asset"); return self.repository.asset(_id(asset_id,"asset"))
    def activities(self,asset_id): self.asset(asset_id); return self.repository.activities(asset_id)
    def save_asset(self,values,asset_id=None):
        self.authorization.require("assets.manage","save an asset"); item=_asset_values(values)
        if item["status"] in self.RETIRED: self.authorization.require("assets.retire","retire an asset")
        self._scope(item)
        if asset_id is None: return self.repository.create_asset(item,self.session.user_id)
        current=self.asset(asset_id)
        if current["church_id"] != item["church_id"]: raise AssetValidationError("An asset cannot be moved to another church.")
        if current["status"] in self.RETIRED and item["status"] not in self.RETIRED: self.authorization.require("assets.retire","restore an asset")
        return self.repository.update_asset(current,item,self.session.user_id)
    def add_activity(self,asset_id,values):
        self.authorization.require("assets.manage","record asset activity"); asset=self.asset(asset_id)
        if asset["status"] in self.RETIRED and values.get("activity_type") not in {"Note","Retirement","Disposal","Loss"}: raise AssetValidationError("Restore this asset before recording ordinary activity.")
        item={"activity_date":values.get("activity_date") or date.today(),"activity_type":_required(values.get("activity_type"),50,"activity type"),"summary":_required(values.get("summary"),500,"summary"),"cost":_money(values.get("cost")),"location_id":_optional_id(values.get("location_id")),"next_action":values.get("next_action") or None,"document_id":_optional_id(values.get("document_id"))}
        if item["location_id"] and self.repository.scope_id("tblAssetLocation",item["location_id"]) != asset["church_id"]: raise AssetValidationError("The resulting location must belong to the asset's church.")
        return self.repository.add_activity(asset,item,self.session.user_id)
    def locations(self,church_id): self.authorization.require("assets.view","view asset locations"); return self.repository.locations(_id(church_id,"church"))
    def create_location(self,church_id,name,address="",note=""):
        self.authorization.require("assets.manage","create an asset location"); return self.repository.create_location(_id(church_id,"church"),_required(name,120,"location name"),_optional(address,255),_optional(note,2000),self.session.user_id)
    def due(self,church_id,days=30): self.authorization.require("assets.view","view maintenance due"); return self.repository.due(_id(church_id,"church"),date.today()+timedelta(days=max(0,min(365,int(days)))))
    def export_csv(self,church_id):
        self.authorization.require("assets.view","export assets")
        return write_csv(self.repository.export_assets(_id(church_id,"church")))
    def preview_csv(self,church_id,content):
        self.authorization.require("assets.manage","preview an asset import"); church_id=_id(church_id,"church")
        context=self.repository.import_context(church_id); locations={r["name"].strip().casefold():r["id"] for r in context["locations"]}; existing_numbers={str(r["value"]).strip().casefold() for r in context["numbers"]}; existing_serials={str(r["value"]).strip().casefold() for r in context["serials"]}; seen_numbers=set(); seen_serials=set(); result=[]
        for line,source in enumerate(read_csv(content),2):
            values={"church_id":church_id,"asset_number":source["Asset Number"],"asset_name":source["Asset Name"],"category":source["Category"],"description":source["Description"],"quantity":source["Quantity"] or 1,"manufacturer":source["Manufacturer"],"model":source["Model"],"serial_number":source["Serial Number"],"location_id":locations.get(source["Location"].casefold()) if source["Location"] else None,"acquisition_method":source["Acquisition Method"],"reference_value":source["Reference Value"],"condition_name":source["Condition"] or "Unknown","status":source["Status"] or "Active","note":source["Note"],"person_id":None,"group_id":None}
            errors=[]; warnings=[]; number=values["asset_number"].strip().casefold(); serial=values["serial_number"].strip().casefold()
            if number in existing_numbers or number in seen_numbers: errors.append("Duplicate asset number")
            if source["Location"] and values["location_id"] is None: errors.append("Location was not found")
            if serial and (serial in existing_serials or serial in seen_serials): warnings.append("Repeated serial number")
            try:
                values.update({
                    "acquisition_date": _csv_date(source["Acquisition Date"]),
                    "warranty_expires": _csv_date(source["Warranty Expires"]),
                    "next_maintenance": _csv_date(source["Next Maintenance"]),
                    "replacement_review": _csv_date(source["Replacement Review"]),
                    "retired_date": _csv_date(source["Retired Date"]),
                })
                values=_asset_values(values)
            except (AssetValidationError,ValueError) as error: errors.append(str(error))
            seen_numbers.add(number)
            if serial: seen_serials.add(serial)
            result.append({"line":line,"source":source,"values":values,"errors":errors,"warnings":warnings})
        return result
    def import_preview(self,preview):
        self.authorization.require("assets.manage","import assets")
        if not preview or any(row["errors"] for row in preview): raise AssetValidationError("Every imported row must be Ready.")
        return self.repository.import_assets([row["values"] for row in preview],self.session.user_id)
    def _scope(self,item):
        for key,table,label in (("location_id","tblAssetLocation","location"),("person_id","tblPerson","person"),("group_id","tblGroup","group")):
            if item.get(key) and self.repository.scope_id(table,item[key]) != item["church_id"]: raise AssetValidationError(f"The responsible {label} must belong to the selected church.")

def _asset_values(values):
    item=dict(values); item["church_id"]=_id(item.get("church_id"),"church"); item["asset_number"]=_required(item.get("asset_number"),40,"asset number"); item["asset_name"]=_required(item.get("asset_name"),160,"asset name"); item["category"]=_required(item.get("category"),80,"category")
    item["quantity"]=int(item.get("quantity") or 1)
    if item["quantity"]<=0: raise AssetValidationError("Quantity must be positive.")
    item["status"] = item.get("status") or "Active"
    if item["status"] not in AssetService.STATUSES: raise AssetValidationError("Select a valid asset status.")
    item["retired_date"] = item.get("retired_date") or None
    if item["status"] in AssetService.RETIRED and not item["retired_date"]: raise AssetValidationError("A retired, lost, or disposed asset requires a date.")
    for key in ("location_id","person_id","group_id"): item[key]=_optional_id(item.get(key))
    for key,limit in (("description",500),("manufacturer",120),("model",120),("serial_number",120),("acquisition_method",40),("condition_name",40),("note",4000)): item[key]=_optional(item.get(key),limit)
    item["reference_value"]=_money(item.get("reference_value"))
    for key in ("acquisition_date","warranty_expires","next_maintenance","replacement_review"): item[key]=item.get(key) or None
    return item
def _id(value,label):
    try: value=int(value)
    except (TypeError,ValueError): raise AssetValidationError(f"A valid {label} is required.")
    if value<=0: raise AssetValidationError(f"A valid {label} is required.")
    return value
def _optional_id(value): return None if value in (None,"") else _id(value,"selection")
def _required(value,limit,label):
    text=str(value or "").strip()
    if not text: raise AssetValidationError(f"{label.title()} is required.")
    if len(text)>limit: raise AssetValidationError(f"{label.title()} is too long.")
    return text
def _optional(value,limit):
    text=str(value or "").strip(); return text[:limit] or None
def _money(value):
    if value in (None,""): return None
    try: result=Decimal(str(value))
    except InvalidOperation: raise AssetValidationError("Enter a valid nonnegative amount.")
    if result<0: raise AssetValidationError("Amounts cannot be negative.")
    return result
def _csv_date(value):
    text=str(value or "").strip()
    if not text:return None
    try:return datetime.strptime(text,"%Y-%m-%d").date()
    except ValueError:raise AssetValidationError(f"Use YYYY-MM-DD for CSV dates: {text}")
