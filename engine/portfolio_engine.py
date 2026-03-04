MAX_POSITIONS = 5
MAX_WEIGHT = 0.35
MIN_WEIGHT = 0.10


def build_portfolio(signals):

    """
    signals örneği:
    [
        {"symbol": "EREGL", "score": 92},
        {"symbol": "TUPRS", "score": 88},
        {"symbol": "ASELS", "score": 84}
    ]
    """

    if not signals:
        return []

    # en yüksek skorlu hisseleri seç
    signals = sorted(signals, key=lambda x: x["score"], reverse=True)
    signals = signals[:MAX_POSITIONS]

    total_score = sum(s["score"] for s in signals)

    portfolio = []

    for s in signals:

        weight = s["score"] / total_score

        # risk sınırları
        if weight > MAX_WEIGHT:
            weight = MAX_WEIGHT

        if weight < MIN_WEIGHT:
            weight = MIN_WEIGHT

        portfolio.append({
            "symbol": s["symbol"],
            "score": s["score"],
            "weight": round(weight * 100, 2)
        })

    return portfolio


def format_portfolio_message(portfolio):

    if not portfolio:
        return "Portföy oluşturulamadı."

    message = "📊 AI PORTFÖY ÖNERİSİ\n\n"

    for p in portfolio:

        message += f"{p['symbol']} | %{p['weight']} | score {p['score']}\n"

    return message
