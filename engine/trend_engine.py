def trend_score(close_series):

    """
    Trend kontrolü
    MA20 > MA50 ise trend yukarı
    """

    if len(close_series) < 50:
        return 0

    ma20 = close_series.tail(20).mean()
    ma50 = close_series.tail(50).mean()

    if ma20 > ma50:
        return 3

    return 0
