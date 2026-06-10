from core.top_signals import get_top_signals

from core.portfolio_health import (
    generate_portfolio_health
)


def generate_alerts():

    report = "🚨 QUANTBIST ALERT CENTER\n\n"

    signals = get_top_signals()

    if signals:

        report += "🔥 TOP BUY SIGNALS\n\n"

        for s in signals[:3]:

            report += (
                f"{s['symbol']}\n"
                f"Signal : {s['signal']}\n"
                f"Score : {s['score']}\n\n"
            )

    report += "📊 PORTFOLIO HEALTH\n\n"

    report += generate_portfolio_health()

    return report