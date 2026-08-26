"""Provider-neutral planning and state for safe external calendar publishing."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from calendar_sources import CalendarEventDescriptor


class CalendarPublicationError(ValueError):
    """Raised when publication state or an adapter result is unsafe."""


@dataclass(frozen=True)
class PublicationDecision:
    """One deterministic action proposed for an external destination."""

    action: str
    descriptor: CalendarEventDescriptor
    source_hash: str
    provider_event_id: str | None = None


def descriptor_hash(descriptor):
    """Return a stable digest of exactly the fields approved for publication."""
    if not isinstance(descriptor, CalendarEventDescriptor):
        raise CalendarPublicationError("Only approved calendar descriptors may be published.")
    payload = {
        "uid": descriptor.uid, "title": descriptor.title,
        "starts_at": descriptor.starts_at.isoformat(),
        "ends_at": descriptor.ends_at.isoformat() if descriptor.ends_at else None,
        "all_day": descriptor.all_day, "time_zone": descriptor.time_zone,
        "location": descriptor.location, "description": descriptor.description,
        "status": descriptor.status, "version": descriptor.version,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class MariaDBCalendarPublicationRepository:
    """Persist publication bindings without credentials or event text."""

    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def bindings(self, provider, destination, uids):
        values = tuple(dict.fromkeys(str(uid) for uid in uids if uid))
        if not values: return {}
        markers = ",".join("?" for _ in values); cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT StableUID,ProviderEventID,LastPublishedVersion,LastPublishedHash,LastResult,Active "
                f"FROM tblCalendarPublication WHERE Provider=? AND DestinationIdentifier=? AND StableUID IN ({markers})",
                (provider, destination, *values))
            return {row[0]: {"provider_event_id": row[1], "version": row[2], "hash": row[3],
                             "result": row[4], "active": bool(row[5])} for row in cursor.fetchall()}
        finally: cursor.close()

    def record_result(self, descriptor, provider, destination, source_hash, result,
                      provider_event_id=None, diagnostic_code=None):
        if result not in {"SUCCESS", "ERROR", "CANCELLED"}:
            raise CalendarPublicationError("The publication result is not approved.")
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "INSERT INTO tblCalendarPublication "
                "(ChurchID,SourceType,SourceID,StableUID,Provider,DestinationIdentifier,ProviderEventID,"
                "LastPublishedVersion,LastPublishedHash,LastPublishedAt,LastResult,SafeDiagnosticCode,Active) "
                "VALUES (?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP(6),?,?,?) "
                "ON DUPLICATE KEY UPDATE ChurchID=VALUES(ChurchID),SourceType=VALUES(SourceType),"
                "SourceID=VALUES(SourceID),ProviderEventID=COALESCE(VALUES(ProviderEventID),ProviderEventID),"
                "LastPublishedVersion=VALUES(LastPublishedVersion),LastPublishedHash=VALUES(LastPublishedHash),"
                "LastPublishedAt=CURRENT_TIMESTAMP(6),LastResult=VALUES(LastResult),"
                "SafeDiagnosticCode=VALUES(SafeDiagnosticCode),Active=VALUES(Active)",
                (descriptor.church_id, descriptor.source_type, descriptor.source_id, descriptor.uid,
                 provider, destination, provider_event_id, descriptor.version, source_hash,
                 result, diagnostic_code, 0 if result == "CANCELLED" else 1))
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()


class CalendarPublicationService:
    """Compare safe source descriptors with stored destination bindings."""

    def __init__(self, repository, authorization, test_mode=False):
        self.repository = repository; self.authorization = authorization; self.test_mode = bool(test_mode)

    def plan(self, provider, destination, descriptors):
        self.authorization.require("calendar.view", "view calendar information")
        self.authorization.require("calendar.publish", "plan calendar publication")
        provider, destination = _required(provider, "provider"), _required(destination, "destination")
        rows = list(descriptors or [])
        if any(not isinstance(row, CalendarEventDescriptor) for row in rows):
            raise CalendarPublicationError("Only approved calendar descriptors may be published.")
        bindings = self.repository.bindings(provider, destination, [row.uid for row in rows])
        decisions = []
        for row in rows:
            digest, binding = descriptor_hash(row), bindings.get(row.uid)
            if row.status == "CANCELLED":
                action = "CANCEL" if binding and binding.get("provider_event_id") else "SKIP"
            elif not binding or not binding.get("provider_event_id") or not binding.get("active"):
                action = "CREATE"
            elif binding.get("hash") != digest or str(binding.get("version")) != str(row.version):
                action = "UPDATE"
            else:
                action = "SKIP"
            decisions.append(PublicationDecision(action, row, digest,
                                                  binding.get("provider_event_id") if binding else None))
        return tuple(decisions)

    def ensure_live_publish_allowed(self):
        """Fail closed before any provider adapter makes a network mutation."""
        self.authorization.require("calendar.publish", "publish calendar events")
        if self.test_mode:
            raise CalendarPublicationError("TEST MODE never publishes to an external calendar.")

    def publish(self, provider_name, destination, decisions, adapter):
        """Execute an approved plan and retain retry-safe per-event results."""
        self.ensure_live_publish_allowed()
        results = []
        for decision in decisions:
            if not isinstance(decision, PublicationDecision):
                raise CalendarPublicationError("The publication plan is invalid.")
            if decision.action == "SKIP":
                results.append((decision, "SKIPPED", None)); continue
            try:
                if decision.action == "CREATE":
                    provider_event_id = adapter.create(destination, decision.descriptor)
                    result = "SUCCESS"
                elif decision.action == "UPDATE":
                    provider_event_id = adapter.update(destination, decision.provider_event_id, decision.descriptor)
                    result = "SUCCESS"
                elif decision.action == "CANCEL":
                    adapter.cancel(destination, decision.provider_event_id)
                    provider_event_id = decision.provider_event_id; result = "CANCELLED"
                else:
                    raise CalendarPublicationError("The publication action is invalid.")
                self.repository.record_result(decision.descriptor, provider_name, destination,
                                              decision.source_hash, result, provider_event_id)
                results.append((decision, result, None))
            except Exception as error:
                code = type(error).__name__[:100]
                self.repository.record_result(decision.descriptor, provider_name, destination,
                                              decision.source_hash, "ERROR",
                                              decision.provider_event_id, code)
                results.append((decision, "ERROR", code))
        return tuple(results)


def _required(value, label):
    result = str(value or "").strip()
    if not result: raise CalendarPublicationError(f"A {label} is required.")
    return result
