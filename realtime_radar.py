import time
from radar_handler import run_radar_cycle

SCAN_INTERVAL = 60  # 1 dakika radar


def start_radar():

    print("🚀 AI TRADING RADAR STARTED")

    while True:

        try:

            print("\n📡 Market taranıyor...")

            start_time = time.time()

            signals = run_radar_cycle()

            scan_time = round(time.time() - start_time, 2)

            if signals:
                print(f"🚨 {len(signals)} sinyal bulundu")

                for s in signals:
                    print(f"{s['ticker']} | {s['signal']} | {s['price']}")

            else:
                print("📊 Sinyal bulunamadı")

            print(f"✅ Tarama süresi: {scan_time} saniye")

        except Exception as e:

            print("❌ Radar hata verdi:", e)

        print(f"⏳ Next scan in {SCAN_INTERVAL} seconds\n")

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    start_radar()
