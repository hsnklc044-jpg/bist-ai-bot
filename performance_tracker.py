import random
import statistics


def get_performance_report():
    # Demo sabit değerler (DB bağlantısız stabil sürüm)
    total_trades = 89
    wins = 44
    losses = 45
    net_profit = -100.0
    current_equity = 99900.0

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "net_profit": net_profit,
        "current_equity": current_equity,
    }


def run_monte_carlo(
    initial_equity=100000,
    win_rate=0.4944,
    avg_win=100,
    avg_loss=-100,
    trades=89,
    simulations=1000,
):
    results = []

    for _ in range(simulations):
        equity = initial_equity

        for _ in range(trades):
            if random.random() < win_rate:
                equity += avg_win
            else:
                equity += avg_loss

        results.append(equity)

    mean_equity = round(statistics.mean(results), 2)
    best_case = round(max(results), 2)
    worst_case = round(min(results), 2)

    ruin_count = sum(1 for r in results if r <= initial_equity * 0.5)
    ruin_probability = round((ruin_count / simulations) * 100, 2)

    return {
        "mean_equity": mean_equity,
        "best_case": best_case,
        "worst_case": worst_case,
        "ruin_probability": ruin_probability,
    }
