def build_ai_portfolio(signals):

    portfolio = []

    for s in signals:

        if s["score"] > 75:

            portfolio.append({
                "ticker": s["ticker"],
                "weight": round(100 / len(signals),2)
            })

    return portfolio
