def decide_trade(signal):

    if signal["score"] > 80 and signal["reward"] > signal["risk"]:
        return "EXECUTE"

    if signal["score"] > 60:
        return "WATCH"

    return "SKIP"
