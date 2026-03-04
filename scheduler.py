import time
import schedule
import datetime

from engine.ultimate_scanner import run_ultimate_scan
from bot import send_telegram_message


def market_is_open():

    now = datetime.datetime.now()

    # hafta sonu çalışmasın
    if now.weekday() >= 5:
        return False

    start = now.replace(hour=10, minute=0, second=0)
    end = now.replace(hour=18, minute=0, second=0)

    return start <= now <= end


def radar_job():

    if not market_is_open():

        print("Piyasa kapalı, radar çalışmadı.")
        return

    print("📡 Radar taraması başladı")

    try:

        signals = run_ultimate_scan()

        for signal in signals:

            send_telegram_message(signal)

    except Exception as e:

        print("Radar hatası:", e)

    print("✅ Radar tamamlandı")


# 15 dakikada bir çalış
schedule.every(15).minutes.do(radar_job)

print("🚀 BIST AI Radar başlatıldı")

while True:

    schedule.run_pending()

    time.sleep(10)
