"""Tests for the optional one-way Google Calendar adapter."""

from datetime import datetime
import unittest

from calendar_sources import CalendarEventDescriptor
from google_calendar_provider import GoogleCalendarProvider, PUBLISH_CREDENTIAL_TARGET, google_event_body


class Request:
    def __init__(self, result): self.result = result
    def execute(self): return self.result


class Events:
    def __init__(self): self.calls = []
    def insert(self, **values): self.calls.append(("insert", values)); return Request({"id": "new-id"})
    def update(self, **values): self.calls.append(("update", values)); return Request({"id": values["eventId"]})


class API:
    def __init__(self): self.events_api = Events()
    def events(self): return self.events_api


def descriptor(**changes):
    values = dict(source_type="CHURCH_EVENT", source_id=2, church_id=1, uid="event-2@churchmanager.local",
                  title="Community Supper", starts_at=datetime(2026, 9, 8, 18), location="Fellowship Hall")
    values.update(changes); return CalendarEventDescriptor(**values)


class GoogleCalendarProviderTests(unittest.TestCase):
    def test_oauth_token_has_a_separate_windows_credential_target(self):
        self.assertEqual(PUBLISH_CREDENTIAL_TARGET, "ChurchManager/GoogleCalendarPublisher")

    def test_body_contains_only_safe_calendar_fields(self):
        body = google_event_body(descriptor())
        self.assertEqual(body["summary"], "Community Supper")
        self.assertEqual(body["start"]["timeZone"], "America/Chicago")
        self.assertEqual(body["extendedProperties"]["private"]["churchManagerUID"], "event-2@churchmanager.local")
        self.assertNotIn("person", str(body).casefold()); self.assertNotIn("token", str(body).casefold())

    def test_create_update_and_cancel_use_expected_api_actions(self):
        api = API(); provider = GoogleCalendarProvider(api); row = descriptor()
        self.assertEqual(provider.create("primary", row), "new-id")
        self.assertEqual(provider.update("primary", "existing", row), "existing")
        provider.cancel("primary", "existing")
        self.assertEqual([item[0] for item in api.events_api.calls], ["insert", "update", "update"])
        self.assertEqual(api.events_api.calls[-1][1]["body"], {"status": "cancelled"})


if __name__ == "__main__": unittest.main()
