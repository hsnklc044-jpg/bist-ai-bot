import yfinance as yf
import pandas as pd
from datetime import datetime


class MarketData:

    def __init__(self):
        self.default_period = "3mo"
        self.default_interval = "1h"

    def get_data(
        self,
        symbol,
        period=None,
        interval=None
    ):

        period = period or self.default_period
        interval = interval or self.default_interval

        try:

            ticker = yf.Ticker(symbol)

            df = ticker.history(
                period=period,
                interval=interval
            )

            if df.empty:
                return None

            df.reset_index(inplace=True)

            return df

        except Exception as e:

            print(f"[MARKET DATA ERROR] {symbol} -> {e}")

            return None

    def get_last_price(self, symbol):

        df = self.get_data(
            symbol,
            period="5d",
            interval="15m"
        )

        if df is None:
            return None

        return round(df["Close"].iloc[-1], 2)

    def prepare_candles(self, df):

        candles = df.copy()

        candles = candles[
            [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]
        ]

        candles.dropna(inplace=True)

        return candles


if __name__ == "__main__":

    md = MarketData()

    data = md.get_data("EREGL.IS")

    if data is not None:

        print(data.tail())

        print(
            "\nLAST PRICE:",
            md.get_last_price("EREGL.IS")
        )