from core.dashboard_data import (
    get_dashboard_stats
)

from core.top_signals import (
    get_top_signals
)

from core.portfolio_report import (
    generate_portfolio_report
)


def generate_summary_report():

    stats = get_dashboard_stats()

    top_signal = "-"

    try:

        signals = get_top_signals()

        if signals:

            top_signal = (
                signals[0]["symbol"]
            )

    except Exception:

        pass

    report = f"""
📊 QUANTBIST SUMMARY

════════════════════

💰 Portfolio Value :
{stats["portfolio"]:,.0f} TL

📂 Positions :
{stats["positions"]}

💵 Cash :
{stats["cash"]} TL

🏆 Top Stock :
{stats["top_stock"]}

════════════════════

⚡ Sharpe :
{stats["sharpe"]}

🎯 Win Rate :
{stats["win_rate"]}%

🏅 Profit Factor :
{stats["profit_factor"]}

📉 Max Drawdown :
{stats["max_drawdown"]}%

════════════════════

🔥 Top Signal :

{top_signal}

"""

    return report