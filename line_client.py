import pprint
import requests


def _post(channel_access_token, endpoint, payload):
    print("=== LINE payload ===")
    pprint.pp(payload)
    print()

    response = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {channel_access_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print("=== LINE API Response ===")
    print(response.status_code)
    print(response.text)
    print()

    response.raise_for_status()


def broadcast_messages(channel_access_token, messages):
    payload = {
        "messages": messages
    }

    _post(
        channel_access_token,
        "https://api.line.me/v2/bot/message/broadcast",
        payload
    )