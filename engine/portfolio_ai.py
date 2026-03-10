def build_portfolio(signals):

    if not signals:
        return []

    # en iyi 5 sinyal
    top = signals[:5]

    total_score = sum([s["ai_score"] for s in top])

    portfolio = []

    for s in top:

        weight = round((s["ai_score"] / total_score) * 100)

        portfolio.append({
            "symbol": s["symbol"],
            "weight": weight,
            "sector": s.get("sector", "UNKNOWN")
        })

    return portfolio
