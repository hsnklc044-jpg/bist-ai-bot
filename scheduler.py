import os
import time
import schedule
import requests

from engine.ultimate_scanner import run_ultimate_scanner


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram gönderim hatası:", e)


def radar_job():

    print("📡 Radar çalışıyor...")

    results = run_ultimate_scanner()

    if not results:

        send_telegram_message("📡 Radar: Güçlü sinyal bulunamadı")

        return

    send_telegram_message("🚨 BIST AI Radar Sonuçları")

    for r in results:
        send_telegram_message(r)


def start_scheduler():

    print("⏰ Radar scheduler başlatıldı")

    # Açılış radar
    schedule.every().day.at("09:55").do(radar_job)

    # Gün ortası radar
    schedule.every().day.at("12:30").do(radar_job)

    # Kapanış radar
    schedule.every().day.at("17:45").do(radar_job)

    while True:

        schedule.run_pending()

        time.sleep(30)


if __name__ == "__main__":

    start_scheduler()
