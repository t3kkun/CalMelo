import copy
import datetime
from zoneinfo import ZoneInfo


JST = ZoneInfo("Asia/Tokyo")


FLEX_TEMPLATE = {
    "type": "bubble",
    "size": "deca",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "text": "",
                        "type": "text",
                        "color": "#FFFFFF",
                        "weight": "bold",
                        "align": "start",
                        "gravity":"center",
                        "wrap": True,
                        "size": "lg",
                        "margin": "lg"
                    }
                ],
                "backgroundColor": "#fe5478",
                "paddingStart": "15px",
                "paddingEnd": "15px",
                "paddingBottom": "md"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "backgroundColor": "#FFFFFF",
                "paddingStart": "20px",
                "paddingEnd": "20px",
                "margin": "sm",
                "paddingBottom": "15px"
            }
        ],
        "paddingAll": "0px",
        "cornerRadius": "md"
    }
}


def event_to_view_model(event):
    start = event["start"]
    end = event["end"]

    is_all_day = "date" in start

    if is_all_day:
        date_str = start["date"]

        start_time = "終日"
        end_time = "終日"

    else:
        start_dt = datetime.datetime.fromisoformat(
            start["dateTime"]
        ).astimezone(JST)

        end_dt = datetime.datetime.fromisoformat(
            end["dateTime"]
        ).astimezone(JST)

        date_str = start_dt.strftime("%Y/%m/%d")

        start_time = start_dt.strftime("%H:%M")
        end_time = end_dt.strftime("%H:%M")

    return {
        "title": event.get("summary", "(no title)"),
        "date": date_str,
        "start_time": start_time,
        "end_time": end_time,
        "description": event.get("description", "")
    }


def build_info_row(label, value):
    return {
        "type": "box",
        "layout": "baseline",
        "spacing": "sm",
        "contents": [
            {
                "type": "text",
                "text": label,
                "color": "#888888",
                "size": "sm",
                "flex": 2
            },
            {
                "type": "text",
                "text": value,
                "wrap": True,
                "size": "sm",
                "flex": 5
            }
        ]
    }


def build_event_flex(view_model):
    bubble = copy.deepcopy(FLEX_TEMPLATE)

    header_text = bubble["body"]["contents"][0]["contents"][0]
    body_contents = bubble["body"]["contents"][1]["contents"]

    header_text["text"] = view_model["title"]

    body_contents.extend([
        build_info_row("日付", view_model["date"]),
        build_info_row("開始", view_model["start_time"]),
        build_info_row("終了", view_model["end_time"]),
    ])

    description = view_model["description"].strip()

    if description:
        body_contents.append({
            "type": "separator",
            "margin": "md"
        })

        body_contents.append({
            "type": "text",
            "text": description[:300],
            "wrap": True,
            "size": "sm",
            "margin": "md"
        })

    return {
        "type": "flex",
        "altText": view_model["title"],
        "contents": bubble
    }


def events_to_flex_messages(events):
    view_models = [
        event_to_view_model(event)
        for event in events
    ]

    return [
        build_event_flex(vm)
        for vm in view_models
    ]