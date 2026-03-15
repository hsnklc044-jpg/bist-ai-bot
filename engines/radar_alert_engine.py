from engines.radar_engine import radar_scan
import time


last_alerts = []


def radar_alert_loop(send_message):

    global last_alerts

    while True:

        try:

            results = radar_scan()

            alerts = []

            for row in results:

                if row["score"] >= 8:

                    alerts.append(row["symbol"])

            new_alerts = [a for a in alerts if a not in last_alerts]

            if new_alerts:

                text = "🚨 Radar Alert\n\n"

                for symbol in new_alerts:

                    text += f"{symbol} ⭐ güçlü radar sinyali\n"

                send_message(text)

            last_alerts = alerts

        except Exception as e:

            print("Radar alert error:", e)

        time.sleep(300)
