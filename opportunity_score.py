def opportunity_score(signal):

    score = 0

    score += signal["score"]

    if signal["reward"] > signal["risk"]:
        score += 20

    if signal["momentum"] > 5:
        score += 10

    if signal["breakout"]:
        score += 10

    return score
