from portfolio_system.portfolio_manager import (
    load_positions,
    remove_position
)

from portfolio_system.pnl_engine import (
    calculate_pnl
)

from portfolio_system.trade_history import (
    save_trade
)


def check_exit(symbol, current_price):

    positions = load_positions()

    if symbol not in positions:

        return None

    position = positions[symbol]

    entry_price = position["entry_price"]

    stop_price = position["stop"]

    target_price = position["target1"]

    pnl = calculate_pnl(
        "LONG",
        entry_price,
        current_price
    )

    exit_reason = None

    if current_price >= target_price:

        exit_reason = "TAKE PROFIT"

    elif current_price <= stop_price:

        exit_reason = "STOP LOSS"

    if exit_reason:

        save_trade(
            symbol,
            entry_price,
            current_price,
            pnl,
            exit_reason
        )

        remove_position(symbol)

        return {

            "symbol": symbol,

            "entry_price": entry_price,

            "exit_price": current_price,

            "reason": exit_reason,

            "pnl": pnl
        }

    return None