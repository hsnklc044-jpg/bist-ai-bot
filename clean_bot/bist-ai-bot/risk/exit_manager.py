from portfolio_system.portfolio_manager import (
    load_positions,
    remove_position
)

from portfolio_system.pnl_engine import calculate_pnl


def check_exit(symbol, current_price):

    positions = load_positions()

    if symbol not in positions:

        return None

    position = positions[symbol]

    signal = position["signal"]
    entry_price = position["entry_price"]
    atr = position["atr"]

    pnl = calculate_pnl(
        signal,
        entry_price,
        current_price
    )

    take_profit = atr * 5
    stop_loss = atr * 2

    exit_reason = None

    if signal == "LONG":

        if current_price >= entry_price + take_profit:

            exit_reason = "TAKE PROFIT"

        elif current_price <= entry_price - stop_loss:

            exit_reason = "STOP LOSS"

    elif signal == "SHORT":

        if current_price <= entry_price - take_profit:

            exit_reason = "TAKE PROFIT"

        elif current_price >= entry_price + stop_loss:

            exit_reason = "STOP LOSS"

    if exit_reason:

        remove_position(symbol)

        return {
            "symbol": symbol,
            "reason": exit_reason,
            "pnl": pnl
        }

    return None