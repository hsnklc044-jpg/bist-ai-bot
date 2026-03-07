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
