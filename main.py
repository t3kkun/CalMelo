from config_loader import load_json

from gcal_client import fetch_tomorrow_events
from formatter import events_to_flex_messages
from line_client import push_messages


GCAL_CREDENTIALS = "credentials/gcal.json"
LINE_CONFIG = "config/line.json"


def main():
    line_config = load_json(LINE_CONFIG)

    events = fetch_tomorrow_events(
        credentials_path=GCAL_CREDENTIALS,
        calendar_id=line_config["calendar_id"]
    )

    if not events:
        print("No events tomorrow")
        return

    messages = events_to_flex_messages(events)

    push_messages(
        channel_access_token=line_config["channel_access_token"],
        to=line_config["to"],
        messages=messages
    )

    print("done")


if __name__ == "__main__":
    main()