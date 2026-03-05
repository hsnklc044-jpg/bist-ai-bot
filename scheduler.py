import schedule
import time

from engine.ultimate_scanner import run_ultimate_scan
from engine.pro_trading_signal_formatter import format_trading_signals

from bot import send_telegram_message, listen_commands


def radar_job():

    try:

        print("🚀 Ultimate Radar başlatılıyor")

        signals = run_ultimate_scan()

        message = format_trading_signals(signals)

        send_telegram_message(message)

    except Exception as e:

        print("Radar job error:", e)


# HER 1 SAATTE RADAR
schedule.every(1).hours.do(radar_job)


def run_scheduler():

    print("📅 Scheduler çalışıyor")

    while True:

        schedule.run_pending()

        time.sleep(5)


if __name__ == "__main__":

    import threading

    threading.Thread(target=listen_commands).start()

    run_scheduler()
