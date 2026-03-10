import yfinance as yf


def get_trade_setup(symbol):

    ticker = f"{symbol}.IS"

    df = yf.download(
        ticker,
        period="3mo",
        interval="1d",
        progress=False
    )

    if df.empty:
        return None

    price = float(df["Close"].iloc[-1])

    support = float(df["Low"].tail(20).min())
    resistance = float(df["High"].tail(20).max())

    entry = round(price, 2)
    stop = round(support * 0.98, 2)
    target = round(resistance * 1.02, 2)

    risk = entry - stop
    reward = target - entry

    rr = round(reward / risk, 2) if risk != 0 else 0

    return entry, stop, target, rr