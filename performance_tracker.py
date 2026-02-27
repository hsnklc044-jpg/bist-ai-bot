import csv
import os
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

FILE_NAME = "trade_log.csv"
START_BALANCE = 100000
GRAPH_FILE = "equity_curve.png"

# ================= INIT =================
def init_log():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Symbol","Entry","Stop","Target",
                "Lot","PositionValue","RR",
                "Status","Result"
            ])

# ================= LOG =================
def log_trade(trade):
    with open(FILE_NAME, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            trade["symbol"],
            trade["entry"],
            trade["stop"],
            trade["target"],
            trade["lot"],
            trade["position_value"],
            trade["rr"],
            "OPEN",
            0
        ])

# ================= RESULT UPDATE =================
def update_trade_results():

    if not os.path.exists(FILE_NAME):
        return

    with open(FILE_NAME, mode="r") as file:
        rows = list(csv.DictReader(file))

    updated = False

    for row in rows:
        if row["Status"] != "OPEN":
            continue

        symbol = row["Symbol"] + ".IS"
        stop = float(row["Stop"])
        target = float(row["Target"])
        position = float(row["PositionValue"])

        df = yf.download(symbol, period="5d", interval="1d", progress=False)
        if df.empty:
            continue

        high = df["High"].max()
        low = df["Low"].min()

        if low <= stop:
            row["Status"] = "CLOSED"
            row["Result"] = -position * 0.01
            updated = True

        elif high >= target:
            row["Status"] = "CLOSED"
            row["Result"] = position * 0.02
            updated = True

    if updated:
        with open(FILE_NAME, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

# ================= EQUITY =================
def calculate_equity_curve():

    balance = START_BALANCE
    curve = [balance]

    if not os.path.exists(FILE_NAME):
        return curve

    with open(FILE_NAME, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            result = float(row["Result"])
            balance += result
            curve.append(balance)

    return curve

# ================= METRICS =================
def performance_metrics():

    update_trade_results()

    wins = 0
    losses = 0
    gross_profit = 0
    gross_loss = 0
    returns = []

    if not os.path.exists(FILE_NAME):
        return {}

    with open(FILE_NAME, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            result = float(row["Result"])
            position = float(row["PositionValue"])

            if position > 0:
                returns.append(result / position)

            if result > 0:
                wins += 1
                gross_profit += result
            elif result < 0:
                losses += 1
                gross_loss += abs(result)

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0

    # Sharpe Ratio
    if len(returns) > 1:
        sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252)
    else:
        sharpe = 0

    # Max Drawdown
    curve = calculate_equity_curve()
    peak = curve[0]
    max_dd = 0

    for equity in curve:
        if equity > peak:
            peak = equity
        dd = peak - equity
        if dd > max_dd:
            max_dd = dd

    total_return = (curve[-1] - START_BALANCE) / START_BALANCE * 100

    return {
        "Total Trades": total_trades,
        "Win Rate (%)": round(win_rate,2),
        "Profit Factor": round(profit_factor,2),
        "Sharpe Ratio": round(sharpe,2),
        "Total Return (%)": round(total_return,2),
        "Max Drawdown (TL)": round(max_dd,2)
    }

# ================= GRAPH =================
def generate_equity_graph():

    update_trade_results()
    curve = calculate_equity_curve()

    plt.figure(figsize=(8,4))
    plt.plot(curve)
    plt.title("Equity Curve")
    plt.xlabel("Trade")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(GRAPH_FILE)
    plt.close()

    return GRAPH_FILE

def get_balance():
    update_trade_results()
    curve = calculate_equity_curve()
    return round(curve[-1], 2)
