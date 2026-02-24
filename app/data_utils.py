import yfinance as yf
import pandas as pd


def get_data(symbol="SISE.IS", period="6mo", interval="1d"):

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=True
        )

        if df is None or df.empty:
            return None

        df = df.dropna()

        df.columns = [col.lower() for col in df.columns]

        return df

    except Exception as e:
        print("DATA ERROR:", e)
        return None
