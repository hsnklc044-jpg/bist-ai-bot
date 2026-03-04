from bot import send_telegram_message, listen_commands
from engine.ultimate_scanner import run_ultimate_scan

import schedule
import time
import threading


# ---------------------------------------------------
# RADAR JOB
# ---------------------------------------------------

def radar_job():

    try:

        print("🚀 Ultimate Radar başlatılıyor")

        send_message("🚀 ULTIMATE BIST AI RADAR BAŞLADI")

        signals = run_ultimate_scan()

        if not signals:

            send_message("Sinyal bulunamadı.")
            return

        for signal in signals[:5]:

            text = f"""
📊 {signal['symbol']}

Fiyat: {signal['price']}

Skor: {signal['score']}

🎯 Hedef: {signal['target']}
🛑 Stop: {signal['stop']}
"""

            send_message(text)

    except Exception as e:

        print("Radar job error:", e)


# ---------------------------------------------------
# SCHEDULE
# ---------------------------------------------------

schedule.every(60).minutes.do(radar_job)


# ---------------------------------------------------
# SCHEDULER LOOP
# ---------------------------------------------------

def run_scheduler():

    print("📅 Scheduler çalışıyor")

    while True:

        try:

            schedule.run_pending()

        except Exception as e:

            print("Scheduler error:", e)

        time.sleep(1)


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

if __name__ == "__main__":

    print("🤖 BIST AI BOT BAŞLADI")

    # Telegram command listener
    thread = threading.Thread(target=listen_commands)
    thread.start()

    # Radar scheduler
    run_scheduler()
