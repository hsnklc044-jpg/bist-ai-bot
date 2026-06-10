from core.top_signals import get_top_signals
from core.rebalancing_engine_v3 import (
    generate_rebalance_report_v3
)
from core.portfolio_allocator_v4 import (
    allocate_portfolio_v4
)


def generate_daily_report():

    report = (
        "📊 QUANTBIST DAILY REPORT\n\n"
    )

    try:

        signals = get_top_signals()

        report += (
            "🔥 TOP SIGNALS\n\n"
        )

        rank = 1

        for s in signals[:5]:

            report += (
                f"{rank}. "
                f"{s['symbol']} "
                f"({s['score']})\n"
            )

            rank += 1

    except Exception:

        report += (
            "TOP SIGNALS ERROR\n"
        )

    report += "\n"

    try:

        report += (
            "💼 ALLOCATION\n\n"
        )

        report += (
            allocate_portfolio_v4(
                100000
            )
        )

    except Exception:

        report += (
            "ALLOCATION ERROR\n"
        )

    report += "\n\n"

    try:

        report += (
            generate_rebalance_report_v3()
        )

    except Exception:

        report += (
            "REBALANCE ERROR\n"
        )

    return report