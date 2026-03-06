def liquidity_score(volume):

    if len(volume) < 20:
        return 0

    score = 0

    avg_vol = volume.tail(20).mean()
    recent_vol = volume.tail(5).mean()

    if recent_vol > avg_vol * 1.5:
        score += 2

    if avg_vol > 500000:
        score += 1

    return score
