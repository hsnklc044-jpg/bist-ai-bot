def ai_score(rsi, volume_spike, trend):

    score = 0

    if rsi < 35:
        score += 40

    if volume_spike > 1.5:
        score += 30

    if trend:
        score += 30

    return score
