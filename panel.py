import os
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("8507109549:AAGekcvM9FbnoFkfJXVCqR4kQTJxzJqbMAQ")


# Ana sayfa
@app.route("/")
def home():
    return "OK"


# Telegram mesaj gönder
def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
    except Exception as e:
        print("Telegram gönderme hatası:", e)


# Webhook (çökmez sürüm)
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    try:
        if request.method == "GET":
            return "Webhook aktif", 200

        data = request.get_json(silent=True)

        if not data:
            return "No JSON", 200

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            if text == "/start":
                send_telegram(chat_id, "🤖 BIST AI aktif.\nSistem çalışıyor.")
            else:
                send_telegram(chat_id, f"Komut: {text}")

        return "ok", 200

    except Exception as e:
        print("WEBHOOK HATA:", e)
        return "error", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
