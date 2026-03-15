from logger_engine import log_info
from radar_engine import start_radar
from report_engine import generate_daily_report
from telegram_engine import send_telegram
from backtest_engine import run_backtest
from tracker_engine import track_trades


def main():

    log_info("BIST AI SYSTEM STARTING")

    report = generate_daily_report()

    send_telegram(report)

    backtest = run_backtest()

    send_telegram(backtest)

    tracker = track_trades()

    send_telegram(tracker)

    start_radar()


if __name__ == "__main__":
    main()
