import time
import os


def run_system():

    while True:

        print("🚀 AUTO SCAN STARTED")

        os.system("python radar_engine.py")

        os.system("python prediction_engine.py")

        os.system("python telegram_signal_engine.py")

        print("✅ SCAN COMPLETE")

        print("⏱ Next scan in 10 minutes")

        time.sleep(600)


if __name__ == "__main__":
    run_system()
