"""CalMelo の手動・定期送信で共通利用する送信サービス。"""

from __future__ import annotations

from typing import Any

from formatter import events_to_flex_messages
from gcal_client import fetch_tomorrow_events
from line_client import push_messages


def send_calendar(channel_access_token: str, calendar_id: str, destination_id: str, credentials_path: str = "credentials/gcal.json") -> int:
    events = fetch_tomorrow_events(credentials_path, calendar_id)
    if not events:
        return 0
    messages = events_to_flex_messages(events)
    push_messages(channel_access_token, destination_id, messages)
    return len(messages)


def send_flex(channel_access_token: str, destination_id: str, message: dict[str, Any]) -> None:
    """Flex MessageまたはFlexコンテナ（bubble / carousel）を送信する。"""
    if message.get("type") in {"bubble", "carousel"}:
        # LINE公式のFlex Message Simulator等が出力するコンテナ形式を許容する。
        # コンテナ自体は変更せず、Push APIに必要なMessageの外側だけを付与する。
        message = {"type": "flex", "altText": "Flex Message", "contents": message}
    elif message.get("type") != "flex":
        raise ValueError("Flex JSONは type: flex のMessage、または type: bubble/carousel のFlexコンテナで入力してください。")
    if not message.get("altText") or not isinstance(message.get("contents"), dict):
        raise ValueError("Flex Messageには altText と contents が必要です。")
    push_messages(channel_access_token, destination_id, [message])


def send_text(channel_access_token: str, destination_id: str, text: str) -> None:
    if not text.strip():
        raise ValueError("送信するテキストを入力してください。")
    push_messages(channel_access_token, destination_id, [{"type": "text", "text": text}])
