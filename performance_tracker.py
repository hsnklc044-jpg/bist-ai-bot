import json
import os
from datetime import datetime

TRADES_FILE = "trades.json"


def load_trades():
    if not os.path.exists(TRADES_FILE):
        return []
    with open(TRADES_FILE, "r") as f:
        return json.load(f)


def save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=4)


def log_trade(symbol, signal_type, entry_price, stop_loss=None, take_profit=None):
    """
    Yeni işlem kaydı oluşturur.
    """

    trades = load_trades()

    trade = {
        "symbol": symbol,
        "signal_type": signal_type,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "open"
    }

    trades.append(trade)
    save_trades(trades)

    return trade


def close_trade(symbol, exit_price):
    """
    Açık işlemi kapatır ve kâr/zarar hesaplar.
    """

    trades = load_trades()

    for trade in trades:
        if trade["symbol"] == symbol and trade["status"] == "open":

            trade["exit_price"] = exit_price
            trade["status"] = "closed"

            if trade["signal_type"] == "BUY":
                trade["pnl"] = round((exit_price - trade["entry_price"]) / trade["entry_price"] * 100, 2)
            else:
                trade["pnl"] = round((trade["entry_price"] - exit_price) / trade["entry_price"] * 100, 2)

            save_trades(trades)
            return trade

    return None


def get_performance():
    """
    Genel performans özeti döndürür.
    """

    trades = load_trades()
    closed = [t for t in trades if t["status"] == "closed"]

    if not closed:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "avg_return": 0
        }

    wins = [t for t in closed if t["pnl"] > 0]
    avg_return = sum(t["pnl"] for t in closed) / len(closed)

    return {
        "total_trades": len(closed),
        "win_rate": round(len(wins) / len(closed) * 100, 2),
        "avg_return": round(avg_return, 2)
    }
