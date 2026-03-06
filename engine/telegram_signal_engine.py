import requests
import os


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_signal(signal):

    if BOT_TOKEN is None or CHAT_ID is None:
        print("Telegram ayarları eksik")
        return

    message = f"""
🚀 BIST AI RADAR

Hisse: {signal['ticker']}
Fiyat: {signal['price']}

Trend: {signal['trend']}
Skor: {signal['score']}/10

Destek: {signal['support']}
Alım: {signal['entry']}
Stop: {signal['stop']}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        requests.post(url, json=payload)

        print("📩 Telegram sinyal gönderildi:", signal["ticker"])

    except Exception as e:

        print("Telegram hata:", e)
