# CalMelo

Google Calendar reminder bot for LINE Messaging API.

## Features

- Google Calendar integration
- LINE Flex Message notification
- Silent mode (skip notification if no events)

## Setup
```bash
uv venv .
```
## Run
```bash
uv run main.py
```

## Web UI

ローカルの運用コンソールを起動するには、次を実行してブラウザで
`http://127.0.0.1:5000` を開きます。外部ネットワークには公開されません。

```bash
uv run webui.py
```

Web UIでは接続設定、宛先（表示名・LINE ID・User/Group・デフォルト宛先）を
管理し、Calendar配信、Flex Message JSON、テキストを手動送信できます。
Flex JSONは `type: "flex"` のLINE Message、またはLINE公式サンプルのような
`type: "bubble"` / `"carousel"` のFlexコンテナを入力できます。後者には送信時に
必要な外側のMessage情報だけが自動で付与されます。

既存の `config/line.json` にある単一の `to` は、宛先を新規登録するまで
デフォルト宛先として互換利用されます。

## Example
<img width="279" height="277" alt="Image" src="https://github.com/user-attachments/assets/c379ae7d-0a62-4945-8fcc-71c4c087c1c2" />

## More
For further information, visit [note](https://note.com/t3kkun/n/nf2e81795e550)
