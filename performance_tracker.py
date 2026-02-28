import json
import os
from datetime import datetime
import yfinance as yf

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


# ==============================
# OPEN TRADES
# ==============================

def check_open_trades():
    trades = _load_trades()
    return [t for t in trades if t["status"] == "open"]


# ==============================
# REAL-TIME PORTFOLIO ENGINE
# ==============================

def get_portfolio_status():

    trades = _load_trades()

    equity = INITIAL_EQUITY
    allocated_capital = 0
    total_unrealized = 0

    for trade in trades:

        if trade["status"] != "open":
            continue

        symbol = trade["symbol"]
        entry = trade["entry_price"]
        stop_distance = trade["stop_distance"]
        lot = trade["lot"]

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")

            if hist.empty:
                continue

            current_price = float(hist["Close"].iloc[-1])

            # ===== STOP CHECK =====
            stop_price = entry - stop_distance

            if current_price <= stop_price:
                trade["status"] = "closed"
                trade["close_price"] = current_price
                trade["close_time"] = datetime.now().isoformat()

                print("STOP HIT:", symbol)
                continue

            # ===== UNREALIZED PNL =====
            unrealized = (current_price - entry) * lot
            total_unrealized += unrealized

            allocated_capital += current_price * lot

        except Exception as e:
            print("PRICE ERROR:", symbol, e)

    # equity güncelle
    equity = INITIAL_EQUITY + total_unrealized

    _save_trades(trades)

    open_trades = [t for t in trades if t["status"] == "open"]

    return {
        "equity": round(equity, 2),
        "total_trades": len(trades),
        "open_positions": len(open_trades),
        "allocated_capital": round(allocated_capital, 2),
        "unrealized_pnl": round(total_unrealized, 2)
    }
