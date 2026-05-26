from core.live_scanner import scan_market
from core.portfolio_checker import check_portfolio

import time
from datetime import datetime

print("🚀 QUANT ENGINE V2.2 STARTED")

while True:

    try:

        print(
            f"\n[{datetime.now()}]"
        )

        print(
            "\n📂 Portfolio Check..."
        )

        check_portfolio()

        print(
            "\n📈 Market Scan..."
        )

        opportunities = scan_market()

        print(
            f"\n✅ SCAN COMPLETE | "
            f"SIGNALS: {len(opportunities)}"
        )

    except Exception as e:

        print(
            f"\n❌ ENGINE ERROR: {e}"
        )

    print(
        "\n⏳ Waiting 300 seconds...\n"
    )

    time.sleep(300)