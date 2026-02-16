import os
from flask import Flask, request
import requests

app = Flask(__name__)

PANEL_PASSWORD = "44Dupduru--"
TELEGRAM_TOKEN = "8507109549:AAG_xNWSP1-g4qlNw78uJyqyyHC80Inin1w"
CHAT_ID = "1790584407"


@app.route("/")
def home():
    return "📊 BIST AI PANEL AKTİF\nBot başarıyla çalışıyor."


# TELEGRAM WEBHOOK
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # CHAT_ID otomatik kaydet
        global CHAT_ID
        CHAT_ID = chat_id

        if text == "/start":
            send_telegram(chat_id, "🤖 BIST AI bot aktif çalışıyor.\nChat ID kaydedildi ✅")
        else:
            send_telegram(chat_id, "Komut alındı: " + text)

    return "ok", 200


# DIŞARIDAN MESAJ GÖNDERME FONKSİYONU
@app.route("/send-test")
def send_test():
    if not CHAT_ID:
        return "CHAT_ID yok", 400

    send_telegram(CHAT_ID, "🚀 Test mesajı başarılı!")
    return "Gönderildi", 200


def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, json=payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
