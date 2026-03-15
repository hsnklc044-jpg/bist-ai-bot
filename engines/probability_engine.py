def trade_probability(rsi, momentum, volume_ratio, score):

    probability = 40

    # RSI zone
    if 55 <= rsi <= 70:
        probability += 15

    # Momentum
    if momentum > 5:
        probability += 15

    # Volume expansion
    if volume_ratio > 2:
        probability += 15

    # AI score
    if score > 100:
        probability += 10

    probability = min(probability,90)

    return probability
