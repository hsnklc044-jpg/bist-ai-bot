import os
import requests
from scanner import scan_market

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        r = requests.post(url, data=payload)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Telegram gönderim hatası:", e)


def build_message(signals):

    message = "🚀 BIST AI RADAR\n\n🔥 TOP SIGNALS\n"

    for s in signals:

        message += f"""
📈 {s['ticker']}

AI Score: {s['score']}
RSI: {s['rsi']}
Volume Spike: {s['volume_spike']}

-----------------
"""

    return message


def run_bot():

    print("Bot başlatıldı")
    print("BIST AI Bot çalışıyor...")

    try:

        signals = scan_market()

        if not signals:
            print("Sinyal bulunamadı")
            return

        message = build_message(signals)

        send_telegram(message)

    except Exception as e:

        print("Bot hata verdi:", e)


if __name__ == "__main__":
    run_bot()
