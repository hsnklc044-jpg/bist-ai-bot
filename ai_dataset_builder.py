def build_dataset(signals):

    X = []
    y = []

    for s in signals:

        features = [
            s["score"],
            s["momentum"],
            s["rsi"],
            s["volume_spike"],
            int(s["breakout"]),
            int(s["smart_money"])
        ]

        X.append(features)

        if s["reward"] > s["risk"]:
            y.append(1)
        else:
            y.append(0)

    return X, y
