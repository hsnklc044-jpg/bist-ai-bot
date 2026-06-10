from core.performance_metrics import (
    generate_performance_metrics
)

from core.alert_engine import (
    generate_alerts
)

from core.market_scan import (
    generate_market_scan
)

from core.rebalancing_engine_v3 import (
    generate_rebalance_report_v3
)


def generate_end_of_day_report():

    report = "🌙 QUANTBIST END OF DAY REPORT\n\n"

    report += "════════════════════\n\n"

    report += generate_performance_metrics()

    report += "\n\n════════════════════\n\n"

    report += generate_alerts()

    report += "\n\n════════════════════\n\n"

    report += generate_market_scan()

    report += "\n\n════════════════════\n\n"

    report += generate_rebalance_report_v3()

    return report