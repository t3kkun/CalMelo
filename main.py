from config_manager import ConfigManager
from sender import send_calendar


GCAL_CREDENTIALS = "credentials/gcal.json"
LINE_CONFIG = "config/line.json"


def main():
    config = ConfigManager(LINE_CONFIG)
    line_config = config.load()
    destination = config.get_default_destination()
    if not destination:
        raise RuntimeError("送信先が未設定です。WebUIから宛先を追加してください。")

    sent_count = send_calendar(
        channel_access_token=line_config["channel_access_token"],
        calendar_id=line_config["calendar_id"],
        destination_id=destination["line_id"],
        credentials_path=GCAL_CREDENTIALS,
    )
    if sent_count == 0:
        print("No events tomorrow")
        return

    print("done")


if __name__ == "__main__":
    main()
