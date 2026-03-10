def generate_alerts(stocks, smart_money, breakouts):

    alerts = []

    smart_symbols = [s["symbol"] for s in smart_money]
    breakout_symbols = [b["symbol"] for b in breakouts]

    for s in stocks:

        symbol = s["symbol"]
        score = s["score"]

        reasons = []

        if score >= 80:
            reasons.append("High AI Score")

        if symbol in smart_symbols:
            reasons.append("Smart Money")

        if symbol in breakout_symbols:
            reasons.append("Breakout")

        if len(reasons) >= 2:

            alerts.append({
                "symbol":symbol,
                "score":score,
                "reason":", ".join(reasons)
            })

    return alerts