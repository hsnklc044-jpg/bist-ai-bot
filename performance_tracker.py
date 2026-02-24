def generate_equity_curve(initial_capital=100000):
    history = load_history()

    equity = initial_capital
    equity_curve = []
    peak = equity
    max_drawdown = 0

    for trade in history:

        if trade["status"] == "TARGET":
            equity *= (1 + trade["rr"] * 0.02)  # %2 risk kuralı

        elif trade["status"] == "STOP":
            equity *= (1 - 0.02)

        equity_curve.append(round(equity, 2))

        if equity > peak:
            peak = equity

        drawdown = (peak - equity) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    total_return = ((equity - initial_capital) / initial_capital) * 100

    return {
        "final_equity": round(equity, 2),
        "total_return": round(total_return, 2),
        "max_drawdown": round(max_drawdown * 100, 2),
        "curve": equity_curve
    }
