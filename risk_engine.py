from sqlalchemy import text
from performance_tracker import engine


def log_trade(symbol, side, entry_price, exit_price, quantity):
    """
    Trade'i DB'ye kaydeder ve profit hesaplar.
    """

    if side.lower() == "long":
        profit = (exit_price - entry_price) * quantity
    elif side.lower() == "short":
        profit = (entry_price - exit_price) * quantity
    else:
        raise ValueError("Side must be 'long' or 'short'")

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO trades 
            (symbol, side, entry_price, exit_price, quantity, profit)
            VALUES (:symbol, :side, :entry_price, :exit_price, :quantity, :profit)
        """), {
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "profit": profit
        })

    return profit
