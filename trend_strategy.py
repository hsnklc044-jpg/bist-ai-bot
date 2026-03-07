def trend_strategy(signal):

    signal["strategy"] = "TREND"

    signal["target"] = round(signal["target"] * 1.1, 2)

    return signal
