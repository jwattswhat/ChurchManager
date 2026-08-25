"""Tests for duplicate-safe provider-neutral calendar publication planning."""

from datetime import datetime
import unittest

from calendar_publication import CalendarPublicationError, CalendarPublicationService, descriptor_hash
from calendar_sources import CalendarEventDescriptor


class Authorization:
    def __init__(self, permissions): self.permissions = set(permissions)
    def require(self, permission, _operation=None):
        if permission not in self.permissions: raise PermissionError(permission)


class Repository:
    def __init__(self, bindings=None): self.values = bindings or {}
    def bindings(self, _provider, _destination, _uids): return self.values


def event(status="CONFIRMED", version="1"):
    return CalendarEventDescriptor("CHURCH_EVENT", 4, 2, "event-4@churchmanager.local", "Church Picnic",
                                   datetime(2026, 9, 1, 12), status=status, version=version)


class CalendarPublicationTests(unittest.TestCase):
    def service(self, bindings=None, test_mode=False):
        return CalendarPublicationService(Repository(bindings), Authorization({"calendar.view", "calendar.publish"}), test_mode)

    def test_new_changed_unchanged_and_cancelled_actions(self):
        row = event(); digest = descriptor_hash(row)
        self.assertEqual(self.service().plan("GOOGLE", "church", [row])[0].action, "CREATE")
        same = {row.uid: {"provider_event_id": "abc", "version": "1", "hash": digest, "active": True}}
        self.assertEqual(self.service(same).plan("GOOGLE", "church", [row])[0].action, "SKIP")
        self.assertEqual(self.service(same).plan("GOOGLE", "church", [event(version="2")])[0].action, "UPDATE")
        self.assertEqual(self.service(same).plan("GOOGLE", "church", [event(status="CANCELLED")])[0].action, "CANCEL")
        self.assertEqual(self.service().plan("GOOGLE", "church", [event(status="CANCELLED")])[0].action, "SKIP")

    def test_permissions_and_test_mode_fail_closed(self):
        denied = CalendarPublicationService(Repository(), Authorization({"calendar.view"}))
        with self.assertRaises(PermissionError): denied.plan("GOOGLE", "church", [event()])
        with self.assertRaises(CalendarPublicationError): self.service(test_mode=True).ensure_live_publish_allowed()

    def test_hash_changes_only_when_safe_payload_changes(self):
        self.assertEqual(descriptor_hash(event()), descriptor_hash(event()))
        self.assertNotEqual(descriptor_hash(event()), descriptor_hash(event(version="2")))
        with self.assertRaises(CalendarPublicationError): descriptor_hash({"title": "unsafe"})


if __name__ == "__main__": unittest.main()
