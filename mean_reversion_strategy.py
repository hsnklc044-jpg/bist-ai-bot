def mean_reversion_strategy(signal):

    signal["strategy"] = "MEAN_REVERSION"

    signal["target"] = round(signal["target"] * 0.9, 2)

    return signal
