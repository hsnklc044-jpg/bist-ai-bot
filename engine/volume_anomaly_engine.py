def volume_anomaly_score(volume_series):

    """
    Hacim patlaması tespit eder
    """

    if len(volume_series) < 20:
        return 0

    avg_volume = volume_series.tail(20).mean()

    last_volume = volume_series.iloc[-1]

    ratio = last_volume / avg_volume

    if ratio > 1.5:
        return 3

    if ratio > 1.2:
        return 2

    if ratio > 1.0:
        return 1

    return 0
