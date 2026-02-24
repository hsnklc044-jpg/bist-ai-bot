import os
import requests
from flask import Flask
from bist30 import scan_bist30

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload)


@app.route("/")
def home():
    return "BIST AI PRO aktif."


@app.route("/morning_scan")
def morning_scan():
    results = scan_bist30()

    if not results:
        return "Sinyal bulunamadı."

    for message in results:
        send_message(message)

    return "Tarama tamamlandı."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
