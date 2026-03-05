import schedule
import time
import threading
from flask import Flask

from engine.ultimate_scanner import ultimate_scanner

app = Flask(__name__)

@app.route("/")
def home():
    return "BIST AI BOT running"


def radar_job():
    print("BIST radar çalışıyor...")
    ultimate_scanner()


def run_scheduler():
    schedule.every(30).minutes.do(radar_job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    thread = threading.Thread(target=run_scheduler)
    thread.start()

    app.run(host="0.0.0.0", port=10000)
