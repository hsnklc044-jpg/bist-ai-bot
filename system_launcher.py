from scanner import scan_market
from signal_filter import filter_signals
from ranking_engine import rank_opportunities
from signal_formatter import format_signal
from telegram_engine import send_telegram


def run_system():

    print("🚀 AI Trading System Starting")

    signals = scan_market()

    if not signals:

        print("No signals found")
        return

    filtered = filter_signals(signals)

    ranked = rank_opportunities(filtered)

    for signal in ranked:

        message = format_signal(signal)

        send_telegram(message)

        print("Signal sent:", signal["ticker"])


if __name__ == "__main__":

    run_system()
