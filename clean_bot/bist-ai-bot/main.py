import time
import yfinance as yf

from core.live_scanner import scan_market
from core.dashboard import print_dashboard

from portfolio_system.portfolio_manager import (
    load_positions
)

from risk.exit_manager import check_exit


print("\n🚀 LIVE INSTITUTIONAL ENGINE STARTED\n")

while True:

    try:

        print("\n========== NEW MARKET CYCLE ==========\n")

        # MARKET SCAN
        scan_market()

        # LOAD POSITIONS
        positions = load_positions()

        # DASHBOARD
        print_dashboard(positions)

        # EXIT CHECK
        for symbol, trade in positions.items():

            try:

                data = yf.download(
                    symbol,
                    period="1d",
                    interval="5m",
                    progress=False
                )

                if data.empty:
                    continue

                current_price = round(
                    float(data["Close"].iloc[-1].item()),
                    2
                )

                result = check_exit(
                    symbol,
                    current_price
                )

                if result:

                    print("\n🚨 POSITION CLOSED")
                    print(result)

            except Exception as e:

                print(f"[EXIT ERROR] {symbol} -> {e}")

        print("\n⏳ Waiting 300 seconds...\n")

        time.sleep(300)

    except Exception as e:

        print(f"\n[MAIN LOOP ERROR] {e}")
        time.sleep(30)