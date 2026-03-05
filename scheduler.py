import time
import schedule

from engine.ultimate_scanner import run_ultimate_scanner
from bot import send_telegram_message


def radar_job():

    try:

        print("🚀 Ultimate Radar başlatılıyor")

        results = run_ultimate_scanner()

        if not results:
            print("Sinyal bulunamadı")
            return

        message = "🚀 BIST AI RADAR\n\n"

        for r in results:
            message += f"{r}\n\n"

        send_telegram_message(message)

        print("📩 Telegram mesajı gönderildi")

    except Exception as e:

        print("Radar job error:", e)


def start():

    print("📡 Scheduler çalışıyor")

    # Her 30 dakikada radar çalışır
    schedule.every(30).minutes.do(radar_job)

    # Başlangıçta bir kez çalıştır
    radar_job()

    while True:

        schedule.run_pending()
        time.sleep(5)
