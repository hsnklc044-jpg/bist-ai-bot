<<<<<<< HEAD
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
=======
from strategy_optimizer import test_rsi_strategy


def optimize_rsi(symbol):

    best_level = 30
    best_score = 0

    for level in [25, 30, 35, 40, 45]:

        score = test_rsi_strategy(symbol, level)

        if score > best_score:

            best_score = score
            best_level = level

    return {
        "best_rsi": best_level,
        "score": round(best_score,2)
    }
>>>>>>> b473b179fde9679eff721a025c85876a830c31be
