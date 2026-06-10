import time
import yfinance as yf

from core.live_scanner import scan_market
# from core.dashboard import print_dashboard

from portfolio_system.portfolio_manager import (
    load_positions
)

from risk.exit_manager import check_exit

from core.telegram_notifier import (
    send_closed_trade
)


print("\n🚀 LIVE INSTITUTIONAL ENGINE STARTED\n")

while True:

    try:

        print(
            "\n========== NEW MARKET CYCLE ==========\n"
        )

        # MARKET SCAN
        scan_market()

        # LOAD POSITIONS
        positions = load_positions()

        # DASHBOARD DISABLED
        print(
            f"OPEN POSITIONS: {len(positions)}"
        )

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
                    float(
                        data["Close"]
                        .iloc[-1]
                        .item()
                    ),
                    2
                )

                result = check_exit(
                    symbol,
                    current_price
                )

                if result:

                    print(
                        "\n🚨 POSITION CLOSED"
                    )

                    print(result)

                    send_closed_trade(
                        result
                    )

            except Exception as e:

                print(
                    f"[EXIT ERROR] "
                    f"{symbol} -> {e}"
                )

        print(
            "\n⏳ Waiting 300 seconds...\n"
        )

        time.sleep(300)

    except Exception as e:

        print(
            f"\n[MAIN LOOP ERROR] {e}"
        )

        time.sleep(30)