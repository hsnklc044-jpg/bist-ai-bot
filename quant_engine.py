def ai_score(rsi, volume_spike, trend, breakout):

    score = 0

    if rsi < 35:
        score += 30

    if volume_spike > 1.5:
        score += 25

    if trend:
        score += 20

    if breakout:
        score += 25

    return score
