import os
import requests

TELEGRAM_TOKEN = 8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I
TELEGRAM_CHAT_ID = 1790584407


def send(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram ENV eksik")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }

    r = requests.post(url, data=data)
    print("Telegram cevap:", r.text)


if __name__ == "__main__":
    send("🔥 BIST AI BOT → GITHUB'TAN MESAJ GELDİ")
