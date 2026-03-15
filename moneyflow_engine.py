import yfinance as yf
from watchlist import BIST_LIST


def money_flow():

    strong = []

    for stock in BIST_LIST:

        try:

            ticker = stock + ".IS"

            df = yf.download(
                ticker,
                period="1mo",
                interval="1d",
                progress=False
            )

            if df is None or len(df) < 20:
                continue

            volume = df["Volume"].iloc[-1]
            volume_avg = df["Volume"].rolling(20).mean().iloc[-1]

            if volume > volume_avg * 1.5:
                strong.append(stock)

        except:
            continue

    return strong
