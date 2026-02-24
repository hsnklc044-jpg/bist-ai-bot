import yfinance as yf
import pandas as pd


def get_data(symbol="SISE.IS", period="6mo", interval="1d"):

    try:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False
        )

        if df is None:
            return None

        if df.empty:
            return None

        df = df.dropna()

        df.columns = [col.lower() for col in df.columns]

        return df

    except Exception as e:
        print("DATA ERROR:", e)
        return None
