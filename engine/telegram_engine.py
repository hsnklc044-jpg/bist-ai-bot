import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_message(message):

    if TELEGRAM_TOKEN is None or CHAT_ID is None:
        print("Telegram bilgileri eksik")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        requests.post(url, json=payload)

        print("Telegram mesaj gönderildi")

    except Exception as e:

        print("Telegram hata:", e)
