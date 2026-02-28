def get_risk_metrics():
    with engine.connect() as conn:
        df = pd.read_sql("""
            SELECT created_at, profit
            FROM trades
            ORDER BY created_at ASC
        """, conn)

    if df.empty:
        return None

    df["return"] = df["profit"] / INITIAL_EQUITY

    # Basic stats
    total_trades = len(df)
    wins = df[df["profit"] > 0]
    losses = df[df["profit"] <= 0]

    win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0

    gross_profit = wins["profit"].sum()
    gross_loss = abs(losses["profit"].sum())

    profit_factor = gross_profit / gross_loss if gross_loss != 0 else float("inf")

    avg_win = wins["profit"].mean() if not wins.empty else 0
    avg_loss = losses["profit"].mean() if not losses.empty else 0

    expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)

    # Sharpe Ratio (simple version)
    if df["return"].std() != 0:
        sharpe = df["return"].mean() / df["return"].std() * (252 ** 0.5)
    else:
        sharpe = 0

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "expectancy": round(expectancy, 2),
        "sharpe": round(sharpe, 2),
    }
