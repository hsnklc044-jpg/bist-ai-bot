from datetime import datetime

from core.daily_summary import generate_daily_summary
from core.top_signals import get_top_signals
from core.telegram_notifier import send_message

last_daily_report = None
last_top_report = None


def run_auto_reports():

    global last_daily_report
    global last_top_report

    now = datetime.now()

    current_day = now.strftime("%Y-%m-%d")
    current_hour = now.hour

    if current_hour == 9:

        if last_daily_report != current_day:

            report = generate_daily_summary()

            send_message(report)

            last_daily_report = current_day

    if current_hour == 18:

        if last_top_report != current_day:

            signals = get_top_signals()

            message = "🔥 TOP AI SIGNALS\n\n"

            rank = 1

            for s in signals:

                message += (
                    f"{rank}. {s['symbol']}\n"
                    f"Score : {s['score']}\n"
                    f"Signal : {s['signal']}\n\n"
                )

                rank += 1

            send_message(message)

            last_top_report = current_day