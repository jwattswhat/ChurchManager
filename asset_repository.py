"""Parameterized MariaDB persistence for congregational assets."""

from __future__ import annotations


class AssetConflictError(RuntimeError):
    """Raised when optimistic asset persistence cannot update one row."""


class MariaDBAssetRepository:
    """Store asset identity, locations, and append-only activity history."""

    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    @staticmethod
    def _rows(cursor):
        names = [item[0] for item in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    def _all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, sql, values)
            return self._rows(cursor)
        finally:
            cursor.close()

    def churches(self):
        return self._all("SELECT ID id,Church name FROM tblChurch ORDER BY Church")

    def choices(self, church_id):
        return {
            "locations": self._all("SELECT ID id,LocationName name FROM tblAssetLocation WHERE ChurchID=? AND IsActive=1 ORDER BY LocationName", (church_id,)),
            "people": self._all("SELECT ID id,TRIM(CONCAT_WS(' ',FirstName,LastName)) name FROM tblPerson WHERE ChurchID=? ORDER BY LastName,FirstName", (church_id,)),
            "groups": self._all("SELECT ID id,Name name FROM tblGroup WHERE ChurchID=? AND Status='ACTIVE' ORDER BY Name", (church_id,)),
            "categories": [{"name": item} for item in self._choice_values("AssetCategory")],
        }

    def list_assets(self, church_id, search="", status=""):
        sql = ("SELECT a.ID id,a.AssetNumber asset_number,a.AssetName asset_name,a.Category category,"
               "COALESCE(l.LocationName,'') location,TRIM(CONCAT_WS(' / ',NULLIF(TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)),''),g.Name)) responsible,"
               "a.`Condition` condition_name,a.Status status,a.NextMaintenanceDate next_maintenance,a.Version version "
               "FROM tblAsset a LEFT JOIN tblAssetLocation l ON l.ID=a.LocationID LEFT JOIN tblPerson p ON p.ID=a.ResponsiblePersonID "
               "LEFT JOIN tblGroup g ON g.ID=a.ResponsibleGroupID WHERE a.ChurchID=?")
        values = [church_id]
        if status:
            sql += " AND a.Status=?"; values.append(status)
        if search:
            sql += " AND (a.AssetNumber LIKE ? OR a.AssetName LIKE ? OR a.SerialNumber LIKE ?)"
            token = f"%{search.strip()}%"; values.extend((token, token, token))
        sql += " ORDER BY a.AssetNumber,a.AssetName"
        return self._all(sql, tuple(values))

    def import_context(self, church_id):
        """Return exact-match values used by reviewed CSV preview."""
        return {
            "locations": self._all(
                "SELECT ID id,LocationName name FROM tblAssetLocation "
                "WHERE ChurchID=? AND IsActive=1", (church_id,)),
            "numbers": self._all(
                "SELECT AssetNumber value FROM tblAsset WHERE ChurchID=?", (church_id,)),
            "serials": self._all(
                "SELECT SerialNumber value FROM tblAsset WHERE ChurchID=? "
                "AND SerialNumber IS NOT NULL AND TRIM(SerialNumber)<>''", (church_id,)),
        }

    def export_assets(self, church_id):
        """Return the approved current-register fields for CSV export."""
        return self._all(
            "SELECT a.AssetNumber `Asset Number`,a.AssetName `Asset Name`,a.Category `Category`,"
            "COALESCE(a.Description,'') `Description`,a.Quantity `Quantity`,"
            "COALESCE(a.Manufacturer,'') `Manufacturer`,COALESCE(a.Model,'') `Model`,"
            "COALESCE(a.SerialNumber,'') `Serial Number`,COALESCE(l.LocationName,'') `Location`,"
            "COALESCE(a.AcquisitionMethod,'') `Acquisition Method`,"
            "COALESCE(a.AcquisitionDate,'') `Acquisition Date`,"
            "COALESCE(a.ReferenceValue,'') `Reference Value`,a.`Condition` `Condition`,"
            "a.Status `Status`,COALESCE(a.WarrantyExpires,'') `Warranty Expires`,"
            "COALESCE(a.NextMaintenanceDate,'') `Next Maintenance`,"
            "COALESCE(a.ReplacementReviewDate,'') `Replacement Review`,"
            "COALESCE(a.RetiredDate,'') `Retired Date`,COALESCE(a.Note,'') `Note` "
            "FROM tblAsset a LEFT JOIN tblAssetLocation l ON l.ID=a.LocationID "
            "WHERE a.ChurchID=? ORDER BY a.AssetNumber,a.AssetName", (church_id,))

    def import_assets(self, rows, user_id):
        """Insert a fully reviewed set as one transaction."""
        cursor = self.connection.cursor()
        try:
            fields = ("ChurchID,AssetNumber,AssetName,Category,Description,Quantity,Manufacturer,Model,"
                      "SerialNumber,LocationID,AcquisitionMethod,AcquisitionDate,ReferenceValue,"
                      "`Condition`,Status,WarrantyExpires,NextMaintenanceDate,ReplacementReviewDate,RetiredDate,Note")
            keys = ("church_id", "asset_number", "asset_name", "category", "description",
                    "quantity", "manufacturer", "model", "serial_number", "location_id",
                    "acquisition_method", "acquisition_date", "reference_value", "condition_name",
                    "status", "warranty_expires", "next_maintenance", "replacement_review",
                    "retired_date", "note")
            for row in rows:
                self._execute(cursor, f"INSERT INTO tblAsset ({fields}) VALUES ({','.join('?' for _ in keys)})",
                              tuple(row.get(key) for key in keys))
                self._audit(cursor, user_id, "ASSET_IMPORTED", cursor.lastrowid)
            self.connection.commit()
            return len(rows)
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def asset(self, asset_id):
        rows = self._all("SELECT ID id,ChurchID church_id,AssetNumber asset_number,AssetName asset_name,Category category,Description description,Quantity quantity,Manufacturer manufacturer,Model model,SerialNumber serial_number,LocationID location_id,ResponsiblePersonID person_id,ResponsibleGroupID group_id,AcquisitionMethod acquisition_method,AcquisitionDate acquisition_date,ReferenceValue reference_value,`Condition` condition_name,Status status,WarrantyExpires warranty_expires,NextMaintenanceDate next_maintenance,ReplacementReviewDate replacement_review,RetiredDate retired_date,Note note,Version version FROM tblAsset WHERE ID=?", (asset_id,))
        return rows[0] if rows else None

    def create_asset(self, values, user_id):
        cursor = self.connection.cursor()
        try:
            fields = ("ChurchID,AssetNumber,AssetName,Category,Description,Quantity,Manufacturer,Model,SerialNumber,LocationID,ResponsiblePersonID,ResponsibleGroupID,AcquisitionMethod,AcquisitionDate,ReferenceValue,`Condition`,Status,WarrantyExpires,NextMaintenanceDate,ReplacementReviewDate,RetiredDate,Note")
            keys = ("church_id","asset_number","asset_name","category","description","quantity","manufacturer","model","serial_number","location_id","person_id","group_id","acquisition_method","acquisition_date","reference_value","condition_name","status","warranty_expires","next_maintenance","replacement_review","retired_date","note")
            self._execute(cursor, f"INSERT INTO tblAsset ({fields}) VALUES ({','.join('?' for _ in keys)})", tuple(values.get(key) for key in keys))
            asset_id = cursor.lastrowid; self._audit(cursor, user_id, "ASSET_CREATED", asset_id)
            self.connection.commit(); return asset_id
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def update_asset(self, current, values, user_id):
        cursor = self.connection.cursor()
        try:
            keys = ("asset_number","asset_name","category","description","quantity","manufacturer","model","serial_number","location_id","person_id","group_id","acquisition_method","acquisition_date","reference_value","condition_name","status","warranty_expires","next_maintenance","replacement_review","retired_date","note")
            columns = ("AssetNumber","AssetName","Category","Description","Quantity","Manufacturer","Model","SerialNumber","LocationID","ResponsiblePersonID","ResponsibleGroupID","AcquisitionMethod","AcquisitionDate","ReferenceValue","`Condition`","Status","WarrantyExpires","NextMaintenanceDate","ReplacementReviewDate","RetiredDate","Note")
            assignments = ",".join(f"{column}=?" for column in columns)
            args = tuple(values.get(key) for key in keys) + (current["id"], current["version"])
            self._execute(cursor, f"UPDATE tblAsset SET {assignments},Version=Version+1 WHERE ID=? AND Version=?", args)
            if cursor.rowcount != 1: raise AssetConflictError("This asset changed. Reopen it and try again.")
            self._audit(cursor, user_id, "ASSET_UPDATED", current["id"]); self.connection.commit(); return True
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def activities(self, asset_id):
        return self._all("SELECT h.ID id,h.ActivityDate activity_date,h.ActivityType activity_type,h.Summary summary,h.Cost cost,l.LocationName location,h.NextActionDate next_action,h.CreatedAt created_at FROM tblAssetActivity h LEFT JOIN tblAssetLocation l ON l.ID=h.LocationID WHERE h.AssetID=? ORDER BY h.ActivityDate DESC,h.ID DESC", (asset_id,))

    def add_activity(self, asset, values, user_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "INSERT INTO tblAssetActivity (AssetID,ActivityDate,ActivityType,Summary,Cost,LocationID,NextActionDate,DocumentID,RecordedByUserID) VALUES (?,?,?,?,?,?,?,?,?)", (asset["id"],values["activity_date"],values["activity_type"],values["summary"],values.get("cost"),values.get("location_id"),values.get("next_action"),values.get("document_id"),user_id))
            activity_id = cursor.lastrowid
            if values.get("location_id") is not None:
                self._execute(cursor, "UPDATE tblAsset SET LocationID=?,Version=Version+1 WHERE ID=?", (values["location_id"],asset["id"]))
            if values.get("next_action") is not None:
                self._execute(cursor, "UPDATE tblAsset SET NextMaintenanceDate=?,Version=Version+1 WHERE ID=?", (values["next_action"],asset["id"]))
            self._audit(cursor,user_id,"ASSET_ACTIVITY_RECORDED",activity_id,"AssetActivity")
            self.connection.commit(); return activity_id
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def locations(self, church_id):
        return self._all("SELECT l.ID id,l.LocationName name,COALESCE(p.LocationName,'') parent,l.Address address,l.IsActive active,l.Note note FROM tblAssetLocation l LEFT JOIN tblAssetLocation p ON p.ID=l.ParentLocationID WHERE l.ChurchID=? ORDER BY l.LocationName", (church_id,))

    def create_location(self, church_id, name, address, note, user_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,"INSERT INTO tblAssetLocation (ChurchID,LocationName,Address,Note) VALUES (?,?,?,?)",(church_id,name,address,note))
            item_id=cursor.lastrowid; self._audit(cursor,user_id,"ASSET_LOCATION_CREATED",item_id,"AssetLocation")
            self.connection.commit(); return item_id
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def due(self, church_id, through_date):
        return self._all("SELECT a.ID id,a.AssetNumber asset_number,a.AssetName asset_name,COALESCE(l.LocationName,'') location,a.NextMaintenanceDate next_maintenance,a.ReplacementReviewDate replacement_review FROM tblAsset a LEFT JOIN tblAssetLocation l ON l.ID=a.LocationID WHERE a.ChurchID=? AND a.Status NOT IN ('Retired','Lost','Disposed') AND (a.NextMaintenanceDate<=? OR a.ReplacementReviewDate<=?) ORDER BY LEAST(COALESCE(a.NextMaintenanceDate,'9999-12-31'),COALESCE(a.ReplacementReviewDate,'9999-12-31')),a.AssetNumber",(church_id,through_date,through_date))

    def scope_id(self, table, item_id):
        rows=self._all(f"SELECT ChurchID church_id FROM {table} WHERE ID=?",(item_id,)); return rows[0]["church_id"] if rows else None

    def _audit(self,cursor,user_id,action,entity_id,entity_type="Asset"):
        self._execute(cursor,"INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID) VALUES (?,?,?,?)",(user_id,action,entity_type,str(entity_id)))

    def _choice_values(self, field):
        rows = self._all("SELECT Choices choices FROM tblChoices WHERE Field=?", (field,))
        text = str(rows[0]["choices"] if rows else "").strip()
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        return [value.strip() for value in text.splitlines() if value.strip()]
