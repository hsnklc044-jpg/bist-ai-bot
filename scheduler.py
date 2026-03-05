import schedule
import time

from engine.ultimate_scanner import run_ultimate_scan
from bot import send_telegram_message


def radar_job():

    try:

        print("🚀 Ultimate Radar başlatılıyor")

        signals = run_ultimate_scan()

        if not signals:
            send_telegram_message("Bugün güçlü sinyal bulunamadı.")
            return

        for s in signals:
            send_telegram_message(s)

    except Exception as e:

        print("Radar job error:", e)


schedule.every(30).minutes.do(radar_job)

print("📅 Scheduler çalışıyor")

while True:
    schedule.run_pending()
    time.sleep(5)
