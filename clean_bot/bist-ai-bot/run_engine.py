from core.live_scanner import scan_market
from core.portfolio_checker import check_portfolio
from core.portfolio_alerts import check_portfolio_alerts
from core.trade_history_engine import process_closed_trades
from core.auto_reports import run_auto_reports
from core.logger import write_log

import time


write_log(
    "ENGINE STARTED"
)

while True:

    try:

        write_log(
            "PORTFOLIO CHECK STARTED"
        )

        check_portfolio()

        write_log(
            "PORTFOLIO CHECK OK"
        )

        write_log(
            "TRADE HISTORY CHECK STARTED"
        )

        process_closed_trades()

        write_log(
            "TRADE HISTORY CHECK OK"
        )

        write_log(
            "PORTFOLIO ALERT CHECK STARTED"
        )

        check_portfolio_alerts()

        write_log(
            "PORTFOLIO ALERT CHECK OK"
        )

        write_log(
            "MARKET SCAN STARTED"
        )

        opportunities = scan_market()

        write_log(
            f"SCAN COMPLETE | SIGNALS={len(opportunities)}"
        )

        write_log(
            "AUTO REPORT CHECK STARTED"
        )

        run_auto_reports()

        write_log(
            "AUTO REPORT CHECK OK"
        )

    except Exception as e:

        write_log(
            f"ENGINE ERROR | {e}"
        )

    write_log(
        "WAITING 300 SECONDS"
    )

    time.sleep(300)