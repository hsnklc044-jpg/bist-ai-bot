def build_portfolio(signals):

    portfolio = []

    if not signals:
        return portfolio

    weight = round(100 / len(signals), 2)

    for s in signals:

        portfolio.append({
            "ticker": s["ticker"],
            "weight": weight
        })

    return portfolio
