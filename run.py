import threading
import time

from engines.radar_engine import radar_scan
from engines.radar_alert_engine import radar_alert_loop
from bot.telegram_notifier import send_telegram
from bot.telegram_bot import main as start_telegram


print("🚀 BIST AI SYSTEM STARTING...")


# RADAR ENGINE
def start_radar():

    print("📡 Radar Engine Started")

    while True:

        try:

            radar = radar_scan()

            print("Radar:", radar)

        except Exception as e:

            print("Radar error:", e)

        time.sleep(600)



# ALERT ENGINE
def start_alerts():

    print("🚨 Radar Alert Engine Started")

    try:

        radar_alert_loop(send_telegram)

    except Exception as e:

        print("Alert error:", e)



# THREADS
radar_thread = threading.Thread(target=start_radar, daemon=True)
alert_thread = threading.Thread(target=start_alerts, daemon=True)

radar_thread.start()
alert_thread.start()


# TELEGRAM BOT (MAIN THREAD)
print("🤖 Telegram Bot Started")

start_telegram()