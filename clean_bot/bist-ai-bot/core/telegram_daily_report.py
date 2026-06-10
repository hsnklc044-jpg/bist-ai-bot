from core.dashboard_data import (
    get_dashboard_stats
)

from core.performance_card import (
    get_performance_metrics
)

from core.rebalancing_engine_v3 import (
    generate_rebalance_report_v3
)


def generate_telegram_daily_report():

    stats = get_dashboard_stats()

    perf = get_performance_metrics()

    rebalance = (
        generate_rebalance_report_v3()
    )

    report = f"""

📊 QUANTBIST DAILY REPORT

💰 Portfolio Value
{stats['portfolio']:,.0f} TL

📦 Positions
{stats['positions']}

🏆 Top Stock
{stats['top_stock']}

📈 Total Return
{perf['total_return']}%

📉 Max Drawdown
{perf['max_drawdown']}%

🎯 Win Rate
{perf['win_rate']}%

🔄 REBALANCE

{rebalance}

"""

    return report