from realtime_engine import get_intraday_data


def intraday_breakout(symbol):

    data = get_intraday_data(symbol)

    if data is None or len(data) < 20:
        return False

    last_price = data["Close"].iloc[-1]

    high20 = data["High"].rolling(20).max().iloc[-2]

    if last_price > high20:
        return True

    return False
