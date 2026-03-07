def adjust_risk(signal):

    if signal["volatility"] > 0.04:
        signal["risk"] *= 0.5

    if signal["score"] > 90:
        signal["risk"] *= 1.2

    return signal
