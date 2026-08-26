"""Optional one-way Google Calendar adapter using locally protected OAuth files."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from credential_store import delete_credential, read_credential, write_credential


SCOPES = (
    "https://www.googleapis.com/auth/calendar.events",
)
OAUTH_DIRECTORY = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ChurchManager" / "OAuth"
CLIENT_SECRET_PATH = OAUTH_DIRECTORY / "client_secret.json"
PUBLISH_CREDENTIAL_TARGET = "ChurchManager/GoogleCalendarPublisher"


class GoogleCalendarProviderError(RuntimeError):
    """Raised when Google Calendar authorization or mutation is unavailable."""


def google_event_body(descriptor):
    """Translate only approved descriptor fields to a Google event body."""
    body = {"summary": descriptor.title, "status": "cancelled" if descriptor.status == "CANCELLED" else "confirmed"}
    if descriptor.location: body["location"] = descriptor.location
    if descriptor.description: body["description"] = descriptor.description
    if descriptor.all_day:
        start = descriptor.starts_at.date(); end = descriptor.ends_at.date() if descriptor.ends_at else start + timedelta(days=1)
        body["start"] = {"date": start.isoformat()}; body["end"] = {"date": end.isoformat()}
    else:
        body["start"] = {"dateTime": descriptor.starts_at.isoformat(), "timeZone": descriptor.time_zone}
        end = descriptor.ends_at or descriptor.starts_at + timedelta(hours=1)
        body["end"] = {"dateTime": end.isoformat(), "timeZone": descriptor.time_zone}
    body["extendedProperties"] = {"private": {"churchManagerUID": descriptor.uid,
                                                  "churchManagerVersion": str(descriptor.version)}}
    return body


class GoogleCalendarProvider:
    """Create, update, and cancel events through an injected Google API service."""

    def __init__(self, service): self.service = service

    def create(self, destination, descriptor):
        result = self.service.events().insert(calendarId=destination, body=google_event_body(descriptor)).execute()
        event_id = result.get("id")
        if not event_id: raise GoogleCalendarProviderError("Google Calendar did not return an event identifier.")
        return event_id

    def update(self, destination, provider_event_id, descriptor):
        if not provider_event_id: raise GoogleCalendarProviderError("The Google event identifier is missing.")
        result = self.service.events().update(calendarId=destination, eventId=provider_event_id,
                                              body=google_event_body(descriptor)).execute()
        return result.get("id") or provider_event_id

    def cancel(self, destination, provider_event_id):
        if not provider_event_id: raise GoogleCalendarProviderError("The Google event identifier is missing.")
        self.service.events().update(calendarId=destination, eventId=provider_event_id,
                                     body={"status": "cancelled"}).execute()


def connect_google_calendar(client_secret_path=CLIENT_SECRET_PATH):
    """Authorize using a token protected by Windows Credential Manager."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as error:
        raise GoogleCalendarProviderError("Google Calendar support is not installed.") from error
    client_secret_path = Path(client_secret_path)
    if not client_secret_path.exists():
        raise GoogleCalendarProviderError("Google Calendar client authorization has not been configured.")
    credentials = None
    protected = read_credential(PUBLISH_CREDENTIAL_TARGET)
    if protected:
        try:
            credentials = Credentials.from_authorized_user_info(
                __import__("json").loads(protected[1]), SCOPES,
            )
        except (TypeError, ValueError):
            delete_credential(PUBLISH_CREDENTIAL_TARGET)
            credentials = None
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
            credentials = flow.run_local_server(port=0)
        write_credential(PUBLISH_CREDENTIAL_TARGET, "oauth", credentials.to_json())
    return GoogleCalendarProvider(build("calendar", "v3", credentials=credentials, cache_discovery=False))
