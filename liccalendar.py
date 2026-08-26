"""Integrate selected ChurchManager scheduling workflows with Google Calendar."""

from __future__ import print_function
import datetime
import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Calendar API scope for read-only access
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
OAUTH_DIRECTORY = Path(
    os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
) / "ChurchManager" / "OAuth"
CLIENT_SECRET_PATH = OAUTH_DIRECTORY / "client_secret.json"
TOKEN_PATH = OAUTH_DIRECTORY / "token.json"


def get_next_sunday():
    """Return the upcoming Sunday's date as a datetime object."""
    today = datetime.datetime.today()
    days_ahead = 6 - today.weekday() if today.weekday() < 6 else 0  # Sunday = 6
    next_sunday = today + datetime.timedelta(days=days_ahead)
    return next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)


def get_week_events(service, sunday):
    """Fetch events from Sunday to following Saturday."""
    next_saturday = sunday + datetime.timedelta(days=6)

    time_min = sunday.isoformat() + "Z"  # Start of Sunday UTC
    time_max = (
        next_saturday + datetime.timedelta(days=1)
    ).isoformat() + "Z"  # End of Saturday

    print(f"Getting events from {sunday.date()} to {next_saturday.date()}")

    events_result = (
        service.events()
        .list(
            calendarId="Life in Christ Lutheran Church",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])
    if not events:
        print("No events found for the week.")
    else:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(f"{start} - {event.get('summary', '(No Title)')}")


def main():
    """Authorize locally and display the coming week's calendar events."""
    OAUTH_DIRECTORY.mkdir(parents=True, exist_ok=True)
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with TOKEN_PATH.open("w", encoding="utf-8") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)

    sunday = get_next_sunday()
    get_week_events(service, sunday)


if __name__ == "__main__":
    main()
