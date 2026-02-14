import os
import requests

TELEGRAM_TOKEN = os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        requests.post(url, data=payload, timeout=10)
        print("Telegram mesajı gönderildi.")
    except Exception as e:
        print("Telegram hatası:", e)


if __name__ == "__main__":
    send_telegram("📊 BIST AI BOT → GitHub entegrasyonu tamam.")
