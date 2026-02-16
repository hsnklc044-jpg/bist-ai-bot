from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

PANEL_PASSWORD = os.getenv("PANEL_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Telegram mesaj gönderme fonksiyonu
def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


# Ana sayfa
@app.route("/")
def home():
    return """
    <h1>BIST AI PANEL AKTİF</h1>
    <p>Bot başarıyla çalışıyor.</p>
    """


# Telegram webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram(chat_id, "🤖 BIST AI bot aktif çalışıyor.")

        elif text == "/panel":
            send_telegram(chat_id, "🔐 Panel şifresi gerekli.")

        else:
            send_telegram(chat_id, "Komut alınamadı.")

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
