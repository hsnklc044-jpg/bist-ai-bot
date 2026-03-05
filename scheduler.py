import threading
import schedule
import time
from engine.ultimate_scanner import run_ultimate_scanner
from telegram_sender import send_message
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "BIST AI BOT running"


def radar_job():

    print("🚀 Ultimate Radar başlatılıyor")

    signals = run_ultimate_scanner()

    if signals:

        message = "🚀 BIST AI RADAR\n\n"

        for s in signals:
            message += s + "\n"

        send_message(message)

    else:
        print("Sinyal yok")


def run_scheduler():

    schedule.every(30).minutes.do(radar_job)

    while True:
        schedule.run_pending()
        time.sleep(5)


threading.Thread(target=run_scheduler).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
