def smart_money_flow(data):

    vol_today = data["Volume"].iloc[-1]
    vol_avg = data["Volume"].rolling(30).mean().iloc[-1]

    if vol_avg == 0:
        return False

    spike = vol_today / vol_avg

    if spike > 2:
        return True

    return False
