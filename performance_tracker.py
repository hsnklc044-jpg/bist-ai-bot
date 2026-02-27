import csv
import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

FILE_NAME = "trade_log.csv"
START_BALANCE = 100000
GRAPH_FILE = "equity_curve.png"

def init_log():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Symbol","Entry","Stop","Target",
                "Lot","PositionValue","RR",
                "Status","Result"
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
            trade["rr"],
            "OPEN",
            0
        ])

def update_trade_results():

    if not os.path.exists(FILE_NAME):
        return

    rows = []
    updated = False

    with open(FILE_NAME, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in rows:
        if row["Status"] != "OPEN":
            continue

        symbol = row["Symbol"] + ".IS"
        entry = float(row["Entry"])
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
