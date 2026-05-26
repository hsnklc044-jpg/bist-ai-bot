def calculate_pnl(signal, entry_price, current_price):

    if signal == "LONG":

        pnl = (
            (current_price - entry_price)
            / entry_price
        ) * 100

    else:

        pnl = (
            (entry_price - current_price)
            / entry_price
        ) * 100

    return round(pnl, 2)