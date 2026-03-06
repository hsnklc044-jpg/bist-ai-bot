def breakout_signal(close, high):

    try:

        if len(high) < 20:
            return False

        resistance = high.tail(20).max()

        last_price = close.iloc[-1]

        if last_price > resistance * 0.995:
            return True

        return False

    except:
        return False
