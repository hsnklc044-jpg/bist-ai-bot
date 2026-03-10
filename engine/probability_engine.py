def trade_probability(score, confidence):

    try:

        probability = (score * 6) + (confidence * 0.4)

        if probability > 95:
            probability = 95

        return round(probability)

    except:

        return 0
