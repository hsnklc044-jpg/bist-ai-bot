def ai_score(rsi, volume_spike, trend, breakout, smart_money, momentum):

    score = 0

    if rsi < 35:
        score += 20

    if volume_spike > 1.5:
        score += 20

    if trend:
        score += 15

    if breakout:
        score += 20

    if smart_money:
        score += 15

    if momentum > 5:
        score += 10

    return score
