import time

from system_launcher import run_system


SCAN_INTERVAL = 300  # saniye (5 dakika)


def start_radar():

    print("📡 REAL-TIME TRADING RADAR STARTED")

    while True:

        try:

            run_system()

        except Exception as e:

            print("Radar error:", e)

        print("Next scan in", SCAN_INTERVAL, "seconds")

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":

    start_radar()
