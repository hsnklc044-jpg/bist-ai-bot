import csv
import os
import matplotlib.pyplot as plt

FILE_NAME = "trade_log.csv"
START_BALANCE = 100000
GRAPH_FILE = "equity_curve.png"

def init_log():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Symbol", "Entry", "Stop",
                "Target", "Lot",
                "PositionValue", "RR"
            ])

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
            trade["rr"]
        ])

def calculate_equity_curve():
    equity = START_BALANCE
    equity_curve = [equity]

    if not os.path.exists(FILE_NAME):
        return equity_curve

    with open(FILE_NAME, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rr = float(row["RR"])
            position = float(row["PositionValue"])
            profit = position * 0.02 * rr  # basit model
            equity += profit
            equity_curve.append(equity)

    return equity_curve

def generate_equity_graph():
    equity_curve = calculate_equity_curve()

    plt.figure(figsize=(8, 4))
    plt.plot(equity_curve)
    plt.title("Equity Curve")
    plt.xlabel("Trade Sayısı")
    plt.ylabel("Sermaye (TL)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(GRAPH_FILE)
    plt.close()

    return GRAPH_FILE

def get_balance():
    curve = calculate_equity_curve()
    return round(curve[-1], 2)
