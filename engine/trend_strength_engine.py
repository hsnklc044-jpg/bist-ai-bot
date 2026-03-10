def trend_strength(close):

    try:

        if len(close) < 50:
            return 0

        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        strength = 0

        if close.iloc[-1] > ma20:
            strength += 1

        if ma20 > ma50:
            strength += 1

        return strength

    except:
        return 0
