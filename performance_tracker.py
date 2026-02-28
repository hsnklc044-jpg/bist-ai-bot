import json
import os
from datetime import datetime
import yfinance as yf

DATA_FILE = "performance_data.json"


# ================= STORAGE =================

def _load():
    if not os.path.exists(DATA_FILE):
        return {
            "initial_capital": 100000,
            "equity": 100000,
            "open_trades": [],
            "closed_trades": []
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ================= OPEN TRADE =================

def log_trade(symbol, entry_price, stop_distance, lot):

    data = _load()

    stop_price = entry_price - stop_distance
    target_price = entry_price + (stop_distance * 2)

    trade = {
        "symbol": symbol,
        "entry_price": entry_price,
        "stop_price": stop_price,
        "target_price": target_price,
        "lot": lot,
        "status": "OPEN",
        "open_date": str(datetime.now())
    }

    data["open_trades"].append(trade)
    _save(data)


# ================= CHECK OPEN TRADES =================

def check_open_trades():

    data = _load()
    updated_open = []

    for trade in data["open_trades"]:

        symbol = trade["symbol"]

        try:
            price = yf.download(symbol, period="1d", auto_adjust=True)["Close"].iloc[-1]
        except:
            updated_open.append(trade)
            continue

        if price <= trade["stop_price"]:
            pnl = (trade["stop_price"] - trade["entry_price"]) * trade["lot"]
            data["equity"] += pnl
            trade["status"] = "STOP_HIT"
            trade["close_price"] = trade["stop_price"]
            trade["pnl"] = pnl
            data["closed_trades"].append(trade)

        elif price >= trade["target_price"]:
            pnl = (trade["target_price"] - trade["entry_price"]) * trade["lot"]
            data["equity"] += pnl
            trade["status"] = "TARGET_HIT"
            trade["close_price"] = trade["target_price"]
            trade["pnl"] = pnl
            data["closed_trades"].append(trade)

        else:
            updated_open.append(trade)

    data["open_trades"] = updated_open
    _save(data)


# ================= BALANCE =================

def get_balance():

    data = _load()

    return {
        "equity": round(data["equity"], 2),
        "total_trades": len(data["closed_trades"]),
        "open_trades": len(data["open_trades"])
    }
