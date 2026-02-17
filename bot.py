import os
import time
import requests

BOT_TOKEN = os.getenv("8507109549:AAGekcvM9FbnoFkfJXVCqR4kQTJxzJqbMAQ")
CHAT_ID = os.getenv("1790584407")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def main():
    send_telegram("🤖 BIST AI BOT AKTİF")

    while True:
        try:
            send_telegram("📊 Sistem çalışıyor...")

        except Exception as e:
            send_telegram(f"Hata: {e}")

        time.sleep(900)  # 15 dk

if __name__ == "__main__":
    main()
