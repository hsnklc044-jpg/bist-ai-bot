<<<<<<< HEAD
def calculate_risk(symbol, entry, stop, capital=100000, risk_percent=2):

    try:

        entry = float(entry)
        stop = float(stop)

        risk_per_share = abs(entry - stop)

        if risk_per_share == 0:
            return None

        max_risk = capital * (risk_percent / 100)

        position_size = max_risk / risk_per_share

        return {
            "symbol": symbol,
            "entry": entry,
            "stop": stop,
            "risk_per_share": round(risk_per_share,2),
            "position_size": int(position_size),
            "max_risk": int(max_risk),
            "risk_percent": risk_percent
        }

    except:

        return None
=======
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
>>>>>>> b473b179fde9679eff721a025c85876a830c31be
