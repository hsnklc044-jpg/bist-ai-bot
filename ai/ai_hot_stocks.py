from ai_trade_radar import scan_trade_radar
from ai_momentum import calculate_momentum
from ai_rsi_radar import scan_rsi_dip
from ai_volume_radar import scan_volume_spike


def get_hot_stocks():

    trade = scan_trade_radar()
    momentum = calculate_momentum()
    rsi = scan_rsi_dip()
    volume = scan_volume_spike()

    scores = {}

    # Trade radar
    for t in trade:
        symbol = t["symbol"]
        scores[symbol] = scores.get(symbol, 0) + 1

    # Momentum radar
    for m in momentum:
        symbol = m["symbol"]
        if m["score"] > 0:
            scores[symbol] = scores.get(symbol, 0) + 1

    # RSI dip
    for r in rsi:
        symbol = r["symbol"]
        scores[symbol] = scores.get(symbol, 0) + 1

    # Volume spike
    for v in volume:
        symbol = v["symbol"]
        scores[symbol] = scores.get(symbol, 0) + 1

    hot = []

    for symbol, score in scores.items():

        if score >= 3:

            hot.append({
                "symbol": symbol,
                "score": score
            })

    hot = sorted(hot, key=lambda x: x["score"], reverse=True)

    return hot[:10]
