import threading
import schedule
import time
from flask import Flask

from engine.ultimate_scanner import run_ultimate_scanner
from telegram_sender import send_message


app = Flask(__name__)


@app.route("/")
def home():
    return "BIST AI BOT running"


def radar_job():

    print("🚀 Ultimate Radar başlatılıyor")

    try:

        signals = run_ultimate_scanner()

        if signals:

            message = "🚀 BIST AI RADAR\n\n"

            for s in signals:
                message += f"{s}\n"

            send_message(message)

            print("Telegram mesajı gönderildi")

        else:
            print("Sinyal yok")

    except Exception as e:

        print("Radar job error:", e)


def run_scheduler():

    print("Scheduler çalışıyor")

    schedule.every(30).minutes.do(radar_job)

    while True:

        schedule.run_pending()
        time.sleep(5)


def start_scheduler():

    thread = threading.Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()


start_scheduler()


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)
