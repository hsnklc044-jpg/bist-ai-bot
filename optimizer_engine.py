from ai_engine import get_ai_score


def optimize_portfolio():

    portfolio = ["ASELS","THYAO","EREGL","KCHOL"]

    results = []

    for symbol in portfolio:

        try:

            score = get_ai_score(symbol)

            if score is None:
                continue

            if score > 80:
                action = "ADD"

            elif score > 60:
                action = "HOLD"

            else:
                action = "REDUCE"

            results.append({
                "symbol": symbol,
                "action": action,
                "score": score
            })

        except:
            continue

    return results