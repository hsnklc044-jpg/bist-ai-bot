import os
from flask import Flask, request
import requests

app = Flask(__name__)

# DOĞRU kullanım
TELEGRAM_TOKEN = os.environ.get("8500392750:AAHprLseYkYGlF6zTw8YJ4doFLqwwvOSjVM")


@app.route("/")
def home():
    return "OK"


def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram(chat_id, "🤖 BIST AI aktif.\nSistem çalışıyor.")
        else:
            send_telegram(chat_id, f"Komut alındı: {text}")

    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
