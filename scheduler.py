import schedule
import time
import threading
import os
from flask import Flask

from engine.ultimate_scanner import ultimate_scanner

app = Flask(__name__)


@app.route("/")
def home():
    return "BIST AI BOT running"


def radar_job():

    print("🚨 BIST radar çalışıyor...")

    try:

        results = ultimate_scanner()

        if results:

            print("Sinyaller bulundu:")

            for r in results:
                print(r)

        else:
            print("Radar sinyal bulamadı")

    except Exception as e:

        print("Radar hata:", e)


def run_scheduler():

    print("Scheduler başlatıldı")

    # BOT BAŞLAR BAŞLAMAZ RADAR
    radar_job()

    # test için 1 dakika
    schedule.every(1).minutes.do(radar_job)

    while True:

        schedule.run_pending()
        time.sleep(1)


# scheduler thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    print("Web server başlatılıyor... Port:", port)

    app.run(host="0.0.0.0", port=port)
