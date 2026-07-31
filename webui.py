"""CalMelo のローカル運用コンソール。"""

from __future__ import annotations

import json
import os

from flask import Flask, flash, redirect, render_template_string, request, url_for

from config_manager import ConfigManager
from sender import send_calendar, send_flex, send_text


BASE = """<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>CalMelo</title>
<style>body{font-family:system-ui,sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;color:#222}nav{display:flex;gap:1rem;border-bottom:1px solid #ddd;padding-bottom:1rem}a{color:#b23b59}form{margin:1.5rem 0}label{display:block;font-weight:600;margin-top:1rem}input,select,textarea,button{box-sizing:border-box;font:inherit;padding:.55rem;margin-top:.35rem;width:100%}textarea{min-height:220px}button{width:auto;background:#b23b59;color:white;border:0;border-radius:4px;padding:.6rem 1.4rem;cursor:pointer}.flash{padding:.75rem;margin:1rem 0;border-radius:4px;background:#e8f5e9}.flash.error{background:#ffebee}table{width:100%;border-collapse:collapse}td,th{padding:.65rem;border-bottom:1px solid #ddd;text-align:left}.inline{display:inline}.inline button{margin:0;width:auto;background:#666}.muted{color:#666;font-size:.9rem}</style></head><body>
<h1>CalMelo</h1><nav><a href=\"{{ url_for('send') }}\">送信</a><a href=\"{{ url_for('destinations') }}\">宛先管理</a><a href=\"{{ url_for('settings') }}\">接続設定</a></nav>
{% with messages=get_flashed_messages(with_categories=true) %}{% for category,message in messages %}<div class=\"flash {{ category }}\">{{ message }}</div>{% endfor %}{% endwith %}
{{ body|safe }}</body></html>"""


def page(body: str, **context: object) -> str:
    return render_template_string(BASE, body=render_template_string(body, **context))


def create_app(config_path: str = "config/line.json") -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("CALMELO_WEBUI_SECRET", "calmelo-local-webui")
    manager = ConfigManager(config_path)

    @app.get("/")
    def send():
        return page("""
        <h2>手動送信</h2>
        {% if destinations %}<form method=\"post\" action=\"{{ url_for('deliver') }}\">
          <label>送信先<select name=\"destination_id\">{% for item in destinations %}<option value=\"{{ item.id }}\" {% if item.id == default_id %}selected{% endif %}>{{ item.name }} ({{ item.kind|capitalize }})</option>{% endfor %}</select></label>
          <fieldset><legend>送信内容</legend>
            <label><input type=\"radio\" name=\"mode\" value=\"calendar\" checked> Calendarチェック + 配信</label>
            <label><input type=\"radio\" name=\"mode\" value=\"flex\"> Flex JSON</label>
            <label><input type=\"radio\" name=\"mode\" value=\"text\"> Text</label>
          </fieldset>
          <div id=\"content-area\" hidden><label id=\"content-label\">入力</label><textarea id=\"content\" name=\"content\"></textarea><p id=\"content-help\" class=\"muted\"></p></div>
          <button type=\"submit\">配信</button>
        </form>
        <script>const radios=document.querySelectorAll('input[name=mode]'),area=document.querySelector('#content-area'),label=document.querySelector('#content-label'),content=document.querySelector('#content'),help=document.querySelector('#content-help');function change(){const m=document.querySelector('input[name=mode]:checked').value;area.hidden=m==='calendar';content.required=m!=='calendar';if(m==='flex'){label.textContent='Flex Message JSON';content.placeholder='{\\n  "type": "bubble",\\n  ...\\n}';help.textContent='LINE公式のbubble/carousel JSON、または type: flex のMessage JSONを入力できます。'}else{label.textContent='テキスト';content.placeholder='送信するメッセージ';help.textContent='そのままテキストメッセージとして送信します。'}}radios.forEach(x=>x.addEventListener('change',change));change();</script>
        {% else %}<p>宛先がありません。<a href=\"{{ url_for('destinations') }}\">宛先管理</a>から追加してください。</p>{% endif %}
        """, destinations=manager.get_destinations(), default_id=(manager.get_default_destination() or {}).get("id"))

    @app.post("/deliver")
    def deliver():
        destination = manager.get_destination(request.form.get("destination_id", ""))
        if not destination:
            flash("送信先を選択してください。", "error")
            return redirect(url_for("send"))
        config = manager.load()
        mode, content = request.form.get("mode"), request.form.get("content", "")
        try:
            if mode == "calendar":
                count = send_calendar(config["channel_access_token"], config["calendar_id"], destination["line_id"])
                flash("翌日の予定はありません。" if count == 0 else f"{count}件の予定を配信しました。")
            elif mode == "flex":
                try:
                    message = json.loads(content)
                except json.JSONDecodeError as error:
                    raise ValueError(f"JSONの形式が正しくありません: {error.msg}") from error
                if not isinstance(message, dict):
                    raise ValueError("Flex JSONはオブジェクトで入力してください。")
                send_flex(config["channel_access_token"], destination["line_id"], message)
                flash("Flex Messageを配信しました。")
            elif mode == "text":
                send_text(config["channel_access_token"], destination["line_id"], content)
                flash("テキストを配信しました。")
            else:
                raise ValueError("不正な送信モードです。")
        except (ValueError, KeyError) as error:
            flash(str(error), "error")
        except Exception:
            app.logger.exception("Delivery failed")
            flash("配信に失敗しました。接続設定とログを確認してください。", "error")
        return redirect(url_for("send"))

    @app.get("/destinations")
    def destinations():
        default = manager.get_default_destination()
        return page("""<h2>宛先管理</h2><p><a href=\"{{ url_for('new_destination') }}\">宛先を追加</a></p>
        {% if items %}<table><tr><th>表示名</th><th>LINE ID</th><th>種別</th><th></th></tr>{% for item in items %}<tr><td>{{ item.name }} {% if item.id == default_id %}<small>（デフォルト）</small>{% endif %}</td><td>{{ item.line_id }}</td><td>{{ item.kind|capitalize }}</td><td><a href=\"{{ url_for('edit_destination', destination_id=item.id) }}\">編集</a> <form class=\"inline\" method=\"post\" action=\"{{ url_for('delete_destination', destination_id=item.id) }}\"><button>削除</button></form>{% if item.id != default_id %} <form class=\"inline\" method=\"post\" action=\"{{ url_for('default_destination', destination_id=item.id) }}\"><button>既定にする</button></form>{% endif %}</td></tr>{% endfor %}</table>{% else %}<p>登録済みの宛先はありません。</p>{% endif %}""", items=manager.get_destinations(), default_id=(default or {}).get("id"))

    @app.route("/destinations/new", methods=["GET", "POST"])
    def new_destination():
        if request.method == "POST":
            try:
                manager.add_destination(request.form["name"], request.form["line_id"], request.form["kind"])
                flash("宛先を追加しました。")
                return redirect(url_for("destinations"))
            except ValueError as error: flash(str(error), "error")
        return destination_form("宛先を追加", None)

    @app.route("/destinations/<destination_id>/edit", methods=["GET", "POST"])
    def edit_destination(destination_id: str):
        item = manager.get_destination(destination_id)
        if not item:
            flash("宛先が見つかりません。", "error"); return redirect(url_for("destinations"))
        if request.method == "POST":
            try:
                manager.update_destination(destination_id, request.form["name"], request.form["line_id"], request.form["kind"])
                flash("宛先を更新しました。"); return redirect(url_for("destinations"))
            except ValueError as error: flash(str(error), "error")
        return destination_form("宛先を編集", item)

    def destination_form(title: str, item: dict[str, str] | None):
        item = item or {"name": "", "line_id": "", "kind": "user"}
        return page("""<h2>{{ title }}</h2><form method=\"post\"><label>表示名<input name=\"name\" value=\"{{ item.name }}\" required></label><label>LINE ID<input name=\"line_id\" value=\"{{ item.line_id }}\" required></label><label>種別<select name=\"kind\"><option value=\"user\" {% if item.kind == 'user' %}selected{% endif %}>User</option><option value=\"group\" {% if item.kind == 'group' %}selected{% endif %}>Group</option></select></label><button>保存</button></form>""", title=title, item=item)

    @app.post("/destinations/<destination_id>/delete")
    def delete_destination(destination_id: str):
        try: manager.delete_destination(destination_id); flash("宛先を削除しました。")
        except KeyError as error: flash(str(error), "error")
        return redirect(url_for("destinations"))

    @app.post("/destinations/<destination_id>/default")
    def default_destination(destination_id: str):
        try: manager.set_default_destination(destination_id); flash("デフォルト宛先を変更しました。")
        except KeyError as error: flash(str(error), "error")
        return redirect(url_for("destinations"))

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        config = manager.load()
        if request.method == "POST":
            manager.update_service_settings(request.form["channel_access_token"], request.form["calendar_id"])
            flash("接続設定を保存しました。"); return redirect(url_for("settings"))
        return page("""<h2>接続設定</h2><form method=\"post\"><label>LINE Channel Access Token<input name=\"channel_access_token\" value=\"{{ config.channel_access_token }}\" required></label><label>Google Calendar ID<input name=\"calendar_id\" value=\"{{ config.calendar_id }}\" required></label><button>保存</button></form>""", config=config)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
