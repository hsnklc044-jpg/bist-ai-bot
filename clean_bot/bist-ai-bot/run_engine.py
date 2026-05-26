from core.live_scanner import scan_market
import time

print("🚀 QUANT ENGINE STARTED")

while True:

    try:

        opportunities = scan_market()

        print(f"\nSCAN COMPLETE | SIGNAL COUNT: {len(opportunities)}")

    except Exception as e:

        print(f"\n[ENGINE ERROR] {e}")

    print("\nWaiting 300 seconds...\n")

    time.sleep(300)