import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly"
]

JST = ZoneInfo("Asia/Tokyo")


def get_access_token(credentials_path):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=SCOPES
    )

    creds.refresh(Request())

    return creds.token


def fetch_tomorrow_events(credentials_path, calendar_id):
    token = get_access_token(credentials_path)

    tomorrow = (
        datetime.datetime.now(JST)
        + datetime.timedelta(days=1)
    ).date()

    start = datetime.datetime.combine(
        tomorrow,
        datetime.time.min,
        tzinfo=JST
    )

    end = datetime.datetime.combine(
        tomorrow,
        datetime.time.max,
        tzinfo=JST
    )

    encoded_calendar_id = quote(calendar_id, safe="")

    url = (
        "https://www.googleapis.com/calendar/v3/"
        f"calendars/{encoded_calendar_id}/events"
    )

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}"
        },
        params={
            "timeMin": start.isoformat(),
            "timeMax": end.isoformat(),
            "singleEvents": "true",
            "orderBy": "startTime"
        }
    )

    print("=== Google Calendar API Response ===")
    print(response.status_code)
    print(response.text)
    print()

    response.raise_for_status()

    return response.json().get("items", [])