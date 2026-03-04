import time
import schedule
import datetime

from engine.ultimate_scanner import run_ultimate_scan
from bot import send_telegram_message


def market_is_open():

    now = datetime.datetime.now()

    if now.weekday() >= 5:
        return False

    start = now.replace(hour=10, minute=0, second=0)
    end = now.replace(hour=18, minute=0, second=0)

    return start <= now <= end


def radar_job():

    if not market_is_open():

        print("Piyasa kapalı. Radar çalışmadı.")
        return

    print("📡 Radar taraması başladı")

    signals = run_ultimate_scan()

    for signal in signals:

        send_telegram_message(signal)

    print("✅ Radar tamamlandı")


# 15 dakikada bir çalıştır
schedule.every(15).minutes.do(radar_job)


print("🚀 AI Radar Scheduler başlatıldı")

while True:

    schedule.run_pending()

    time.sleep(10)
