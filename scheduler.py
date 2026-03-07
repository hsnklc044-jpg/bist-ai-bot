import requests
import time
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        r = requests.post(url, data=data)
        print("Telegram mesaj gönderildi:", r.text)
    except Exception as e:
        print("Telegram hata:", e)

def run_bot():
    print("BIST AI Bot çalışıyor...")
    send_telegram("🤖 BIST AI Bot aktif ve çalışıyor!")

if __name__ == "__main__":
    print("Bot başlatıldı")

    while True:
        run_bot()
        time.sleep(3600)  # 1 saat
