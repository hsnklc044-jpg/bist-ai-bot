def liquidity_score(volume):

    if len(volume) < 20:
        return 0

    avg_volume = volume.tail(20).mean()
    recent_volume = volume.tail(5).mean()

    score = 0

    # hacim artışı
    if recent_volume > avg_volume * 1.5:
        score += 2

    # minimum likidite kontrolü
    if avg_volume > 500000:
        score += 1

    return score
