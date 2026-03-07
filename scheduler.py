import requests
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    r = requests.post(url, data=data)
    print("Telegram response:", r.text)


def run_bot():
    print("Bot başlatıldı")
    print("BIST AI Bot çalışıyor...")

    send_telegram("🤖 BIST AI Bot test mesajı")


if __name__ == "__main__":
    run_bot()
