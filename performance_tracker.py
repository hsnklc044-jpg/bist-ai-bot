import json
import os
import math
from datetime import datetime
import matplotlib.pyplot as plt

DATA_FILE = "performance_data.json"

# ================= STORAGE =================

def _load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "initial_capital": 100000,
            "equity_curve": [],
            "trades": []
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ================= TRADE LOG =================

def log_trade(symbol, signal_type, entry_price, stop_loss=None, take_profit=None):
    data = _load_data()

    trade = {
        "symbol": symbol,
        "signal_type": signal_type,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pnl": 0
    }

    data["trades"].append(trade)

    # Simüle edilmiş PnL (örnek sistem için)
    simulated_return = 0.02  # %2 varsayalım (engine'e bağlayabiliriz)
    pnl = entry_price * simulated_return

    last_equity = data["equity_curve"][-1] if data["equity_curve"] else data["initial_capital"]
    new_equity = last_equity + pnl

    data["equity_curve"].append(new_equity)

    _save_data(data)


# ================= BALANCE =================

def get_balance():
    data = _load_data()

    equity_curve = data["equity_curve"]
    initial = data["initial_capital"]

    if not equity_curve:
        return {
            "equity": initial,
            "daily_pnl": 0,
            "total_pnl": 0
        }

    current_equity = equity_curve[-1]
    total_pnl = current_equity - initial

    daily_pnl = 0
    if len(equity_curve) > 1:
        daily_pnl = equity_curve[-1] - equity_curve[-2]

    return {
        "equity": round(current_equity, 2),
        "daily_pnl": round(daily_pnl, 2),
        "total_pnl": round(total_pnl, 2)
    }


# ================= METRICS =================

def performance_metrics():
    data = _load_data()
    equity = data["equity_curve"]

    if len(equity) < 2:
        return {
            "max_drawdown": 0,
            "sharpe": 0
        }

    returns = []
    for i in range(1, len(equity)):
        r = (equity[i] - equity[i - 1]) / equity[i - 1]
        returns.append(r)

    avg_return = sum(returns) / len(returns)
    std_dev = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns))

    sharpe = 0
    if std_dev != 0:
        sharpe = (avg_return / std_dev) * math.sqrt(252)

    # Max Drawdown
    peak = equity[0]
    max_dd = 0

    for value in equity:
        if value > peak:
            peak = value
        dd = (peak - value) / peak
        if dd > max_dd:
            max_dd = dd

    return {
        "max_drawdown": round(max_dd * 100, 2),
        "sharpe": round(sharpe, 2)
    }


# ================= GRAPH =================

def generate_equity_graph():
    data = _load_data()
    equity = data["equity_curve"]

    if not equity:
        return

    plt.figure()
    plt.plot(equity)
    plt.title("Equity Curve")
    plt.xlabel("Trade")
    plt.ylabel("Equity")
    plt.tight_layout()
    plt.savefig("equity_curve.png")
    plt.close()
