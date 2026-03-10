def momentum_score(data):

    try:

        price_now = data["Close"].iloc[-1]
        price_10 = data["Close"].iloc[-10]
        price_20 = data["Close"].iloc[-20]

        roc10 = (price_now - price_10) / price_10
        roc20 = (price_now - price_20) / price_20

        momentum = (roc10 * 0.6) + (roc20 * 0.4)

        return round(momentum * 100, 2)

    except:

        return 0
