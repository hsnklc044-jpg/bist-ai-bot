def orderflow_score(close, volume):

    if len(close) < 20:
        return 0

    score = 0

    # hacim hızlanması
    vol_recent = volume.tail(5).mean()
    vol_old = volume.tail(20).head(10).mean()

    if vol_recent > vol_old * 1.5:
        score += 2

    # momentum hızlanması
    momentum = close.iloc[-1] / close.iloc[-5]

    if momentum > 1.03:
        score += 2

    # price acceleration
    accel = close.pct_change().tail(5).mean()

    if accel > 0.01:
        score += 1

    return score
