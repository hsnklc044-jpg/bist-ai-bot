from core.performance_metrics import (
    generate_performance_metrics
)

from core.market_scan import (
    generate_market_scan
)

from core.alert_engine import (
    generate_alerts
)

from core.portfolio_report import (
    generate_portfolio_report
)


def generate_morning_report():

    report = "🌅 QUANTBIST MORNING REPORT\n\n"

    report += "════════════════════\n\n"

    report += generate_performance_metrics()

    report += "\n\n════════════════════\n\n"

    report += generate_alerts()

    report += "\n\n════════════════════\n\n"

    report += generate_market_scan()

    report += "\n\n════════════════════\n\n"

    report += generate_portfolio_report()

    return report