from core.portfolio_report import (
    generate_portfolio_report
)

from core.performance_report import (
    generate_performance_report
)


def generate_daily_summary():

    portfolio = (
        generate_portfolio_report()
    )

    performance = (
        generate_performance_report()
    )

    report = (

        "📈 DAILY SUMMARY\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "💼 PORTFOLIO STATUS\n\n"

        f"{portfolio}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "📊 PERFORMANCE\n\n"

        f"{performance}"
    )

    return report