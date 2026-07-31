"""LINE 設定の読み書きを一元化するためのライブラリ。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4


class ConfigManager:
    """CalMelo の設定ファイルを管理する。"""

    def __init__(self, path: str | Path = "config/line.json") -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "channel_access_token": "",
                "calendar_id": "",
                "destinations": [],
                "default_destination_id": None,
            }
        with self.path.open("r", encoding="utf-8") as file:
            config = json.load(file)
        config.setdefault("channel_access_token", "")
        config.setdefault("calendar_id", "")
        config.setdefault("destinations", [])
        config.setdefault("default_destination_id", None)
        return config

    def save(self, config: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=2)
            file.write("\n")

    def update_service_settings(self, channel_access_token: str, calendar_id: str) -> None:
        config = self.load()
        config["channel_access_token"] = channel_access_token.strip()
        config["calendar_id"] = calendar_id.strip()
        self.save(config)

    def get_destinations(self) -> list[dict[str, str]]:
        config = self.load()
        destinations = list(config["destinations"])
        # 既存の単一宛先設定も、編集するまで利用できるようにする。
        if not destinations and config.get("to"):
            return [{"id": "legacy-default", "name": "デフォルト宛先", "line_id": config["to"], "kind": "user"}]
        return destinations

    def get_destination(self, destination_id: str) -> dict[str, str] | None:
        return next((item for item in self.get_destinations() if item["id"] == destination_id), None)

    def get_default_destination(self) -> dict[str, str] | None:
        config = self.load()
        destination_id = config.get("default_destination_id")
        if destination_id:
            destination = self.get_destination(destination_id)
            if destination:
                return destination
        destinations = self.get_destinations()
        return destinations[0] if destinations else None

    def add_destination(self, name: str, line_id: str, kind: str) -> dict[str, str]:
        destination = self._validated_destination(name, line_id, kind)
        destination["id"] = str(uuid4())
        config = self.load()
        config["destinations"].append(destination)
        if not config.get("default_destination_id"):
            config["default_destination_id"] = destination["id"]
        self.save(config)
        return destination

    def update_destination(self, destination_id: str, name: str, line_id: str, kind: str) -> None:
        config = self.load()
        for index, destination in enumerate(config["destinations"]):
            if destination["id"] == destination_id:
                updated = self._validated_destination(name, line_id, kind)
                updated["id"] = destination_id
                config["destinations"][index] = updated
                self.save(config)
                return
        raise KeyError("宛先が見つかりません。")

    def delete_destination(self, destination_id: str) -> None:
        config = self.load()
        before = len(config["destinations"])
        config["destinations"] = [item for item in config["destinations"] if item["id"] != destination_id]
        if len(config["destinations"]) == before:
            raise KeyError("宛先が見つかりません。")
        if config.get("default_destination_id") == destination_id:
            config["default_destination_id"] = config["destinations"][0]["id"] if config["destinations"] else None
        self.save(config)

    def set_default_destination(self, destination_id: str) -> None:
        if not self.get_destination(destination_id):
            raise KeyError("宛先が見つかりません。")
        config = self.load()
        config["default_destination_id"] = destination_id
        self.save(config)

    @staticmethod
    def _validated_destination(name: str, line_id: str, kind: str) -> dict[str, str]:
        name, line_id = name.strip(), line_id.strip()
        if not name or not line_id:
            raise ValueError("表示名とLINE IDは必須です。")
        if kind not in {"user", "group"}:
            raise ValueError("種別はUserまたはGroupを指定してください。")
        return {"name": name, "line_id": line_id, "kind": kind}
