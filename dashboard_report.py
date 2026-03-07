def generate_dashboard(metrics):

    report = f"""
📊 AI TRADING DASHBOARD

Total Trades: {metrics['trades']}

Wins: {metrics['wins']}
Losses: {metrics['losses']}

Win Rate: {metrics['win_rate']}%

Average Return: {metrics['avg_return']}%
"""

    return report
