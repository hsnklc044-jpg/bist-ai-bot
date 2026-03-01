def get_risk_metrics():
    win_rate = 49.44
    profit_factor = 0.98
    avg_win = 100.0
    avg_loss = -100.0
    expectancy = -1.12
    sharpe_ratio = -0.01

    return {
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "sharpe_ratio": sharpe_ratio,
    }
