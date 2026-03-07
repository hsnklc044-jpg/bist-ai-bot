def filter_signals(signals):

    filtered = []

    for s in signals:

        if s["score"] > 70 and s["reward"] > s["risk"]:

            filtered.append(s)

    return filtered
