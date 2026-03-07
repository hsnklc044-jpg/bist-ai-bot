from performance_engine import get_stats


def generate_report():

    stats = get_stats()

    report = f"""
📊 BOT PERFORMANCE

Total Signals: {stats['signals']}

Wins: {stats['wins']}
Losses: {stats['loss']}

Win Rate: %{stats['win_rate']}
"""

    return report
