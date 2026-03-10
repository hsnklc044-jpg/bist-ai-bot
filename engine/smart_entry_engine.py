def detect_entry(close, high, low):

    if len(close) < 20:
        return None

    last_price = close.iloc[-1]

    resistance = high.tail(20).max()
    support = low.tail(20).min()

    # BREAKOUT
    if last_price > resistance * 0.995:
        return "BREAKOUT"

    # PULLBACK
    if last_price < support * 1.02:
        return "PULLBACK"

    # TREND CONTINUATION
    ma20 = close.tail(20).mean()

    if last_price > ma20:
        return "TREND"

    return None
