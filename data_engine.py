import yfinance as yf
from watchlist import BIST_LIST


def get_market_data():

    try:

        tickers = " ".join([s + ".IS" for s in BIST_LIST])

        df = yf.download(
            tickers,
            period="6mo",
            interval="1d",
            group_by="ticker",
            progress=False,
            threads=True
        )

        return df

    except:

        return None
