from scanner import scan_market
from signal_filter import filter_signals
from ranking_engine import rank_opportunities
from signal_formatter import format_signal
from telegram_engine import send_telegram
from logger_engine import log_info


def run_system():

    log_info("System scan started")

    signals = scan_market()

    if not signals:

        log_info("No signals found")
        return

    filtered = filter_signals(signals)

    ranked = rank_opportunities(filtered)

    for signal in ranked:

        message = format_signal(signal)

        send_telegram(message)

        log_info(f"Signal sent: {signal['ticker']}")
