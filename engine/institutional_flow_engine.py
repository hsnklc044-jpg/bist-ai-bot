def institutional_flow(volume, close):

    try:

        if len(volume) < 20:
            return 0

        avg_volume = volume.tail(20).mean()

        last_volume = volume.iloc[-1]

        momentum = close.iloc[-1] / close.iloc[-5]

        score = 0

        if last_volume > avg_volume * 2:
            score += 2

        if momentum > 1.03:
            score += 2

        return score

    except:

        return 0
