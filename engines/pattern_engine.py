def detect_pattern(data):

    try:

        highs = data["High"]
        lows = data["Low"]

        last_high = highs.iloc[-1]
        prev_high = highs.iloc[-2]

        last_low = lows.iloc[-1]
        prev_low = lows.iloc[-2]

        if last_high > prev_high and last_low > prev_low:
            return "ASCENDING"

        if last_high < prev_high and last_low < prev_low:
            return "DESCENDING"

        return "RANGE"

    except:

        return "UNKNOWN"
