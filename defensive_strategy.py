def defensive_strategy(signal):

    signal["strategy"] = "DEFENSIVE"

    signal["risk"] = round(signal["risk"] * 0.5, 2)

    return signal
