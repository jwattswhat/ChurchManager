"""Transactionally install validated, metadata-only lectionary packages."""

from __future__ import annotations

from dataclasses import dataclass

from bulletin_orders import portable_connection
from lectionary_packages import (
    LectionaryPackageError,
    LectionaryPackageValidator,
    load_lectionary_package,
)


@dataclass(frozen=True)
class LectionaryImportResult:
    """Non-sensitive result returned after a successful package transaction."""

    package_id: int
    package_code: str
    package_version: str
    action: str
    system_count: int
    edition_count: int
    cycle_count: int
    proper_count: int
    appointment_count: int


def _key(value):
    return str(value).strip().casefold()


class LectionaryPackageImporter:
    """Install one complete package while protecting local and foreign records."""

    def __init__(self, connection, validator=None):
        self.connection = portable_connection(connection)
        self.validator = validator or LectionaryPackageValidator()

    def install_path(self, path, church_id=None, primary_edition_key=None):
        """Load, validate, and install a checksum-protected JSON package."""
        package, checksum = load_lectionary_package(path)
        return self.install(package, checksum, church_id, primary_edition_key)

    def install(self, package, checksum, church_id=None, primary_edition_key=None):
        """Install or upgrade a package in one transaction."""
        summary = self.validator.validate(package, checksum)
        cursor = self.connection.cursor()
        try:
            cursor.execute("START TRANSACTION")
            package_id, action = self._package(cursor, package, checksum)
            self._retire_owned_catalog(cursor, package_id)
            edition_ids = {}
            for system in package["systems"]:
                system_id = self._system(cursor, package_id, system)
                for edition in system["editions"]:
                    edition_id = self._edition(cursor, package_id, system_id, edition)
                    edition_ids[_key(edition["edition_key"])] = edition_id
                    cycle_ids = self._cycles(cursor, edition_id, edition.get("cycles", []))
                    for proper in edition["propers"]:
                        proper_id = self._proper(
                            cursor, package_id, system_id, edition_id, cycle_ids, proper,
                        )
                        self._appointments(cursor, package_id, proper_id, proper["appointments"])
            if primary_edition_key is not None:
                self._set_primary_edition(
                    cursor, church_id, primary_edition_key, edition_ids,
                )
            cursor.execute(
                "INSERT INTO tblLectionaryPackageImport "
                "(LectionaryPackageID,PackageVersion,Checksum,Action,SystemCount,"
                "EditionCount,CycleCount,ProperCount,AppointmentCount) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (package_id, summary.package_version, checksum, action,
                 summary.system_count, summary.edition_count, summary.cycle_count,
                 summary.proper_count, summary.appointment_count),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
        return LectionaryImportResult(
            package_id, summary.package_code, summary.package_version, action,
            summary.system_count, summary.edition_count, summary.cycle_count,
            summary.proper_count, summary.appointment_count,
        )

    @staticmethod
    def _one(cursor, sql, values=()):
        cursor.execute(sql, values)
        return cursor.fetchone()

    def _package(self, cursor, package, checksum):
        code = _key(package["package_code"])
        row = self._one(
            cursor, "SELECT ID FROM tblLectionaryPackage WHERE PackageCode=? FOR UPDATE",
            (code,),
        )
        values = (
            package["package_version"], package["title"], package["source_name"],
            package["source_reference"], package["package_notice"],
            package["distribution_scope"], checksum,
        )
        if row:
            package_id = row[0]
            cursor.execute(
                "UPDATE tblLectionaryPackage SET PackageVersion=?,Title=?,SourceName=?,"
                "SourceReference=?,PackageNotice=?,DistributionScope=?,Checksum=?,"
                "IsActive=1 WHERE ID=?",
                values + (package_id,),
            )
            return package_id, "UPGRADE"
        cursor.execute(
            "INSERT INTO tblLectionaryPackage "
            "(PackageCode,PackageVersion,Title,SourceName,SourceReference,PackageNotice,"
            "DistributionScope,Checksum) VALUES (?,?,?,?,?,?,?,?)", (code,) + values,
        )
        return cursor.lastrowid, "INSTALL"

    @staticmethod
    def _retire_owned_catalog(cursor, package_id):
        cursor.execute("UPDATE tblReading SET IsActive=0 WHERE PackageID=?", (package_id,))
        cursor.execute("UPDATE tblPropers SET IsActive=0 WHERE PackageID=?", (package_id,))
        cursor.execute("UPDATE tblLectionaryEdition SET IsActive=0 WHERE PackageID=?", (package_id,))
        cursor.execute("UPDATE tblLectionarySystem SET Active=0 WHERE PackageID=?", (package_id,))

    def _owned_row(self, cursor, table, key_column, key, package_id):
        row = self._one(
            cursor, f"SELECT ID,PackageID FROM {table} WHERE {key_column}=? FOR UPDATE",
            (key,),
        )
        if row and row[1] != package_id:
            raise LectionaryPackageError(
                f"Stable key {key} is already owned by another source."
            )
        return row[0] if row else None

    def _system(self, cursor, package_id, system):
        key = _key(system["system_key"])
        system_id = self._owned_row(
            cursor, "tblLectionarySystem", "SystemCode", key, package_id,
        )
        editions = system["editions"]
        cycle_count = max((len(item.get("cycles", [])) for item in editions), default=0)
        cycle_type = "None" if cycle_count == 0 else ("ABC" if cycle_count == 3 else "Custom")
        values = (system["name"], cycle_type, system.get("note") or None, package_id)
        if system_id:
            cursor.execute(
                "UPDATE tblLectionarySystem SET Name=?,CycleType=?,Note=?,PackageID=?,"
                "Active=1,IsStarter=1 WHERE ID=?", values + (system_id,),
            )
            return system_id
        cursor.execute(
            "INSERT INTO tblLectionarySystem "
            "(SystemCode,Name,CycleType,Active,Note,PackageID,IsStarter) "
            "VALUES (?, ?, ?,1,?, ?,1)", (key,) + values,
        )
        return cursor.lastrowid

    def _edition(self, cursor, package_id, system_id, edition):
        key = _key(edition["edition_key"])
        edition_id = self._owned_row(
            cursor, "tblLectionaryEdition", "EditionCode", key, package_id,
        )
        values = (
            system_id, edition["name"], edition.get("edition_year"),
            str(edition["status"]).upper(), edition.get("valid_from") or None,
            edition.get("valid_through") or None, package_id,
            edition.get("source_note") or None, edition.get("resolver_version") or "1",
            edition.get("cycle_rule") or "none",
        )
        if edition_id:
            cursor.execute(
                "UPDATE tblLectionaryEdition SET LectionarySystemID=?,Name=?,EditionYear=?,"
                "Status=?,ValidFrom=?,ValidThrough=?,PackageID=?,IsStarter=1,IsActive=1,"
                "SourceNote=?,ResolverVersion=?,CycleRule=? WHERE ID=?", values + (edition_id,),
            )
            return edition_id
        cursor.execute(
            "INSERT INTO tblLectionaryEdition "
            "(EditionCode,LectionarySystemID,Name,EditionYear,Status,ValidFrom,ValidThrough,"
            "PackageID,IsStarter,IsActive,SourceNote,ResolverVersion,CycleRule) "
            "VALUES (?,?,?,?,?,?,?,?,1,1,?,?,?)",
            (key,) + values,
        )
        return cursor.lastrowid

    def _cycles(self, cursor, edition_id, cycles):
        cursor.execute(
            "UPDATE tblLectionaryCycle SET IsActive=0,Sequence=1000000+ID "
            "WHERE LectionaryEditionID=?",
            (edition_id,),
        )
        result = {}
        for cycle in cycles:
            key = _key(cycle["cycle_key"])
            row = self._one(
                cursor, "SELECT ID FROM tblLectionaryCycle "
                "WHERE LectionaryEditionID=? AND CycleCode=? FOR UPDATE",
                (edition_id, key),
            )
            values = (cycle["display_name"], cycle["sequence"], int(cycle["is_active"]))
            if row:
                cycle_id = row[0]
                cursor.execute(
                    "UPDATE tblLectionaryCycle SET DisplayName=?,Sequence=?,IsActive=? WHERE ID=?",
                    values + (cycle_id,),
                )
            else:
                cursor.execute(
                    "INSERT INTO tblLectionaryCycle "
                    "(LectionaryEditionID,CycleCode,DisplayName,Sequence,IsActive) "
                    "VALUES (?,?,?,?,?)", (edition_id, key) + values,
                )
                cycle_id = cursor.lastrowid
            result[key] = cycle_id
        return result

    def _proper(self, cursor, package_id, system_id, edition_id, cycle_ids, proper):
        key = _key(proper["proper_key"])
        proper_id = self._owned_row(cursor, "tblPropers", "ProperKey", key, package_id)
        cycle_key = _key(proper["cycle_key"]) if proper.get("cycle_key") else ""
        cycle_id = cycle_ids.get(cycle_key)
        cycle_label = cycle_key.upper() or None
        values = (
            system_id, edition_id, cycle_id, key, cycle_label, proper["sort"],
            proper.get("season") or None, proper["liturgical_date"],
            proper.get("default_color") or None, proper.get("alternate_color") or None,
            proper.get("calendar_rule") or None, package_id, proper.get("note") or None,
        )
        if proper_id:
            cursor.execute(
                "UPDATE tblPropers SET LectionarySystemID=?,LectionaryEditionID=?,"
                "LectionaryCycleID=?,ProperKey=?,Cycle=?,Sort=?,Season=?,LiturgicalDate=?,"
                "Color=?,AltColor=?,CalendarRule=?,PackageID=?,IsStarter=1,IsActive=1,"
                "Theme='',Note=NULL,SourceNote=? WHERE ID=?", values + (proper_id,),
            )
            return proper_id
        cursor.execute(
            "INSERT INTO tblPropers "
            "(LectionarySystemID,LectionaryEditionID,LectionaryCycleID,ProperKey,Cycle,Sort,"
            "Season,LiturgicalDate,Color,AltColor,CalendarRule,PackageID,IsStarter,IsActive,"
            "Theme,Note,SourceNote) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1,1,'',NULL,?)", values,
        )
        return cursor.lastrowid

    def _appointments(self, cursor, package_id, proper_id, appointments):
        ids = {}
        for item in appointments:
            key = _key(item["appointment_key"])
            appointment_id = self._owned_row(
                cursor, "tblReading", "AppointmentKey", key, package_id,
            )
            values = (
                proper_id, key, str(item["role"]).upper(), item["display_role"],
                item["display_role"], item["display_citation"], item["display_citation"],
                item["normalized_citation"], item.get("track_code") or None,
                item.get("option_group_code") or None, str(item["option_type"]).upper(),
                item["sequence"], int(item["is_default"]), package_id,
                item.get("note") or None,
            )
            if appointment_id:
                cursor.execute(
                    "UPDATE tblReading SET PropersID=?,AppointmentKey=?,Role=?,DisplayRole=?,"
                    "Reading=?,Reference=?,DisplayCitation=?,NormalizedCitation=?,TrackCode=?,"
                    "OptionGroupCode=?,OptionType=?,PairedAppointmentID=NULL,Sequence=?,"
                    "IsDefault=?,PackageID=?,IsStarter=1,IsActive=1,Note=? WHERE ID=?",
                    values + (appointment_id,),
                )
            else:
                cursor.execute(
                    "INSERT INTO tblReading "
                    "(PropersID,AppointmentKey,Role,DisplayRole,Reading,Reference,DisplayCitation,"
                    "NormalizedCitation,TrackCode,OptionGroupCode,OptionType,PairedAppointmentID,"
                    "Sequence,IsDefault,PackageID,IsStarter,IsActive,Note) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,NULL,?,?,?,1,1,?)", values,
                )
                appointment_id = cursor.lastrowid
            ids[key] = appointment_id
        for item in appointments:
            paired = item.get("paired_appointment_key")
            if paired:
                cursor.execute(
                    "UPDATE tblReading SET PairedAppointmentID=? WHERE ID=?",
                    (ids[_key(paired)], ids[_key(item["appointment_key"])]),
                )

    @staticmethod
    def _set_primary_edition(cursor, church_id, edition_key, edition_ids):
        if church_id is None:
            raise LectionaryPackageError(
                "A church must be selected when setting the primary lectionary edition."
            )
        edition_id = edition_ids.get(_key(edition_key))
        if edition_id is None:
            raise LectionaryPackageError(
                "The requested primary edition is not in the installed package."
            )
        cursor.execute(
            "UPDATE tblChurch SET PrimaryLectionaryEditionID=? WHERE ID=?",
            (edition_id, church_id),
        )
        if cursor.rowcount != 1:
            raise LectionaryPackageError("The selected church is unavailable.")
