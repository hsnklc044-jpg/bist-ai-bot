def position_size(portfolio, risk_percent, entry, stop):

    risk_amount = portfolio * (risk_percent / 100)

    stop_distance = abs(entry - stop)

    if stop_distance == 0:
        return 0

    size = risk_amount / stop_distance

    return int(size)
