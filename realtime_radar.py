import time
from radar_handler import run_radar_cycle

SCAN_INTERVAL = 60

<<<<<<< HEAD
=======

>>>>>>> b473b179fde9679eff721a025c85876a830c31be
def start_radar():

    print("🚀 AI TRADING RADAR STARTED")

    while True:

<<<<<<< HEAD
        print("")
        print("🔎 Market taranıyor...")

        run_radar_cycle()

        print("")
=======
        run_radar_cycle()

>>>>>>> b473b179fde9679eff721a025c85876a830c31be
        print("Next scan in", SCAN_INTERVAL, "seconds")

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
<<<<<<< HEAD
    start_radar()
=======
    start_radar()
>>>>>>> b473b179fde9679eff721a025c85876a830c31be
