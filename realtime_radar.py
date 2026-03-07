import time
from radar_handler import run_radar_cycle

SCAN_INTERVAL = 300  # 5 dakika


def start_radar():

    print("🚀 AI TRADING RADAR STARTED")

    while True:

        print("\n📡 Starting market scan...")

        start_time = time.time()

        try:
            run_radar_cycle()

        except Exception as e:
            print("❌ Radar error:", e)

        scan_time = round(time.time() - start_time, 2)

        print(f"✅ Scan completed in {scan_time} seconds")
        print(f"⏳ Next scan in {SCAN_INTERVAL} seconds\n")

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    start_radar()
