import json
from ai_engine import get_ai_score


def analyze_portfolio():

    try:

        with open("portfolio.json") as f:
            portfolio = json.load(f)

    except:
        return None

    results = []

    for symbol, qty in portfolio.items():

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
                "score": score,
                "action": action
            })

        except:
            continue

    return results