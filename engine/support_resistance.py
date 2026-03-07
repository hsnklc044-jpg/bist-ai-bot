import pandas as pd

def calculate_support(data):

    return data["Low"].rolling(20).min().iloc[-1]


def calculate_resistance(data):

    return data["High"].rolling(20).max().iloc[-1]


def calculate_trade_levels(data):

    support = calculate_support(data)
    resistance = calculate_resistance(data)

    entry = support * 1.01
    stop = support * 0.97
    target = resistance

    risk = ((entry - stop) / entry) * 100
    reward = ((target - entry) / entry) * 100

    return {
        "support": round(support,2),
        "entry": round(entry,2),
        "stop": round(stop,2),
        "target": round(target,2),
        "risk": round(risk,2),
        "reward": round(reward,2)
    }
