def adaptive_score(close, volume):

    try:

        score = 0

        # momentum
        momentum = close.iloc[-1] / close.iloc[-10]

        if momentum > 1.05:
            score += 3
        elif momentum > 1.02:
            score += 2
        else:
            score += 1

        # hacim gücü
        avg_volume = volume.tail(20).mean()
        last_volume = volume.iloc[-1]

        if last_volume > avg_volume * 2:
            score += 3
        elif last_volume > avg_volume * 1.5:
            score += 2
        else:
            score += 1

        return score

    except:

        return 0
