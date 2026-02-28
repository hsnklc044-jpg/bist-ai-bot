import json
import os
from datetime import datetime

TRADES_FILE = "trades.json"
INITIAL_EQUITY = 100000


# ==============================
# DOSYA KONTROL
# ==============================

def _ensure_file():
    if not os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "w") as f:
            json.dump([], f)


def _load_trades():
    _ensure_file()
    with open(TRADES_FILE, "r") as f:
        return json.load(f)


def _save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=4)


# ==============================
# TRADE LOG
# ==============================

def log_trade(symbol, entry_price, stop_distance, lot):
    try:
        trade = {
            "symbol": str(symbol),
            "entry_price": float(entry_price),
            "stop_distance": float(stop_distance),
            "lot": float(lot),
            "open_time": datetime.now().isoformat(),
            "status": "open"
        }

        trades = _load_trades()
        trades.append(trade)
        _save_trades(trades)

        print("TRADE LOGGED:", symbol)

    except Exception as e:
        print("TRADE LOG ERROR:", e)


# ==============================
# AÇIK POZİSYON KONTROL
# ==============================

def check_open_trades():
    trades = _load_trades()
    open_trades = [t for t in trades if t["status"] == "open"]

    print("AÇIK POZİSYON SAYISI:", len(open_trades))
    return open_trades


# ==============================
# BALANCE HESAPLAMA
# ==============================

def get_portfolio_status():
    trades = _load_trades()

    open_trades = [t for t in trades if t["status"] == "open"]

    total_allocation = sum(t["entry_price"] * t["lot"] for t in open_trades)

    equity = INITIAL_EQUITY

    return {
        "equity": equity,
        "total_trades": len(trades),
        "open_positions": len(open_trades),
        "allocated_capital": total_allocation
    }
