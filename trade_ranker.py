def rank_trades(signals, volume_leaders, momentum_leaders, smart_money):

    ranked = []

    volume_tickers = [v["ticker"] for v in volume_leaders]
    momentum_tickers = [m["ticker"] for m in momentum_leaders]
    smart_tickers = [s["ticker"] for s in smart_money]

    for s in signals:

        score = 0

        if s["ticker"] in volume_tickers:
            score += 30

        if s["ticker"] in momentum_tickers:
            score += 30

        if s["ticker"] in smart_tickers:
            score += 25

        score += s["confidence"]

        ranked.append({
            "ticker": s["ticker"],
            "entry": s["entry"],
            "rsi": s["rsi"],
            "score": score,
            "signal": s["signal"]
        })

    ranked = sorted(
        ranked,
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked[:3]
