import requests
import os

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print("TOKEN:", TOKEN)
print("CHAT_ID:", CHAT_ID)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    r = requests.post(url, data=payload)

    print("Telegram response:", r.text)


def run_bot():
    print("Bot başlatıldı")
    print("BIST AI Bot çalışıyor...")

    send_telegram("🤖 BIST AI Bot aktif!")


if __name__ == "__main__":
    run_bot()
