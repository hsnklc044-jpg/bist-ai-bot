import time
from radar_handler import run_radar_cycle

SCAN_INTERVAL = 300


def start_radar():

    print("🚀 AI TRADING RADAR STARTED")

    while True:

        run_radar_cycle()

        print("Next scan in", SCAN_INTERVAL, "seconds")

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":

    start_radar()
