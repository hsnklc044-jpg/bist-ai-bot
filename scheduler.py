import requests
import time
import os

# Environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("==== DEBUG BILGILERI ====")
print("TOKEN:", TOKEN)
print("CHAT_ID:", CHAT_ID)
print("=========================")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": msg
        }

        print("API URL:", url)

        r = requests.post(url, data=data)

        print("Telegram response:", r.text)

    except Exception as e:
        print("Telegram gönderme hatası:", e)


def run_bot():
    print("BIST AI Bot çalışıyor...")
    send_telegram("🤖 BIST AI Bot test mesajı")


if __name__ == "__main__":
    print("Bot başlatıldı")

    run_bot()
