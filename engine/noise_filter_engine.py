def noise_filter(close, volume):

    if len(close) < 20:
        return False

    # minimum hacim
    avg_volume = volume.tail(20).mean()

    if avg_volume < 500000:
        return False

    # volatilite kontrolü
    volatility = close.pct_change().abs().tail(10).mean()

    if volatility > 0.08:
        return False

    # momentum gücü
    momentum = close.iloc[-1] / close.iloc[-10]

    if momentum < 1.02:
        return False

    return True
