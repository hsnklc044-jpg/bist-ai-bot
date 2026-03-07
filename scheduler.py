import requests
import time
import os

# Render environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": msg
        }

        r = requests.post(url, data=data)
        print("Telegram response:", r.text)

    except Exception as e:
        print("Telegram gönderme hatası:", e)


def run_bot():
    print("BIST AI Bot çalışıyor...")
    send_telegram("🤖 BIST AI Bot aktif ve çalışıyor!")


if __name__ == "__main__":
    print("Bot başlatıldı")

    while True:
        run_bot()
        time.sleep(3600)  # 1 saat bekler
