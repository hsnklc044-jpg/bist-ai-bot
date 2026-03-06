import pandas as pd


def calculate_entry(df):

    close = df["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    close = pd.to_numeric(close, errors="coerce").dropna()

    if len(close) < 50:
        return None

    price = float(close.iloc[-1])

    support = float(close.tail(20).min())

    entry = round(support * 1.01, 2)

    stop = round(support * 0.97, 2)

    target = round(entry + (entry - stop) * 3, 2)

    return {
        "price": round(price, 2),
        "support": round(support, 2),
        "entry": entry,
        "stop": stop,
        "target": target
    }
