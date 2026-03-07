def calculate_metrics(trades):

    total_trades = len(trades)

    wins = sum(1 for t in trades if t > 0)

    losses = sum(1 for t in trades if t <= 0)

    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

    avg_return = sum(trades) / total_trades if total_trades > 0 else 0

    return {
        "trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate,2),
        "avg_return": round(avg_return,2)
    }
