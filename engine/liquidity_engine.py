def liquidity_score(volume):

    if len(volume) < 30:
        return 0

    avg_volume = volume.tail(20).mean()

    last_volume = volume.iloc[-1]

    score = 0

    # hacim spike
    if last_volume > avg_volume * 2:
        score += 3

    elif last_volume > avg_volume * 1.5:
        score += 2

    elif last_volume > avg_volume * 1.2:
        score += 1

    return score
