from core.portfolio_health import (
    generate_portfolio_health
)

from core.top_signals import (
    get_top_signals
)


def generate_market_scan():

    report = "🔍 QUANTBIST MARKET SCAN\n\n"

    signals = get_top_signals()

    report += "🔥 TOP SIGNALS\n\n"

    rank = 1

    for s in signals[:5]:

        report += (
            f"{rank}. {s['symbol']}\n"
            f"Score : {s['score']}\n"
            f"Signal : {s['signal']}\n\n"
        )

        rank += 1

    report += "\n📊 PORTFOLIO HEALTH\n\n"

    report += generate_portfolio_health()

    return report