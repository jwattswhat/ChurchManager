"""Integrate selected ChurchManager scheduling workflows with Google Calendar."""

from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Calendar API scope for read-only access
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


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
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret_565047851417-o4acc580v6bjeh1ekoddt5q47lgdt2id.apps.googleusercontent.com.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)

    sunday = get_next_sunday()
    get_week_events(service, sunday)


if __name__ == "__main__":
    main()
