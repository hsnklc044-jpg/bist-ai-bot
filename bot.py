import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_message(message):

    if TELEGRAM_TOKEN is None or CHAT_ID is None:
        print("Telegram ayarları eksik")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:

        r = requests.post(url, json=payload)

        if r.status_code != 200:
            print("Telegram hata:", r.text)

    except Exception as e:

        print("Telegram gönderim hatası:", e)
