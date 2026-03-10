def extract_features(signal):

    return [
        signal["score"],
        signal["momentum"],
        signal["rsi"],
        signal["volume_spike"],
        int(signal["breakout"]),
        int(signal["smart_money"])
    ]
