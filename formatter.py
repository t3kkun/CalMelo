from copy import deepcopy
from datetime import datetime


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
                        "type": "text",
                        "text": "",
                        "color": "#FFFFFF",
                        "weight": "bold",
                        "align": "start",
                        "gravity": "center",
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
    },

    "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
        {
            "type": "separator"
        },
        {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "GitHub",
                            "uri": "https://github.com/t3kkun/CalMelo?openExternalBrowser=1"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "note",
                            "uri": "https://note.com/t3kkun?openExternalBrowser=1"
                        }
                    }
                ],
                "margin": "md"
            }
        ]
    }
}


def parse_datetime(dt_str):
    return datetime.fromisoformat(
        dt_str.replace("Z", "+00:00")
    )


def create_event_flex(event):
    bubble = deepcopy(FLEX_TEMPLATE)

    title = event.get("summary", "No Title")

    start_raw = event["start"]["dateTime"]
    end_raw = event["end"]["dateTime"]

    start = parse_datetime(start_raw)
    end = parse_datetime(end_raw)

    start_time = start.strftime("%H:%M")
    end_time = end.strftime("%H:%M")

    date = start.strftime("%Y/%m/%d")

    description = event.get("description", "")

    # title
    bubble["body"]["contents"][0]["contents"][0]["text"] = title

    detail_contents = [
        {
            "type": "text",
            "text": f"日付：{date}",
            "weight": "bold",
            "wrap": True
        },
        {
            "type": "text",
            "text": f"開始時刻：{start_time}",
            "weight": "bold",
            "wrap": True
        },
        {
            "type": "text",
            "text": f"終了時刻：{end_time}",
            "weight": "bold",
            "wrap": True
        }
    ]

    if description:
        detail_contents.extend([
            {
                "type": "separator",
                "margin": "lg"
            },
            {
                "type": "text",
                "text": description,
                "wrap": True,
                "margin": "lg"
            }
        ])

    bubble["body"]["contents"][1]["contents"] = detail_contents

    return {
        "type": "flex",
        "altText": f"予定: {title}",
        "contents": bubble
    }


def events_to_flex_messages(events):
    return [create_event_flex(event) for event in events]