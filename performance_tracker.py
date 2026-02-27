import csv
import os

FILE_NAME = "trade_log.csv"
START_BALANCE = 100000

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

def get_balance():
    if not os.path.exists(FILE_NAME):
        return START_BALANCE

    balance = START_BALANCE

    with open(FILE_NAME, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rr = float(row["RR"])
            position = float(row["PositionValue"])
            balance += position * 0.02 * rr

    return round(balance, 2)
