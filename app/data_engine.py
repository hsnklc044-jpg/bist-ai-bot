import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


class DataEngine:

    def __init__(self):
        self.period = "6mo"
        self.interval = "1d"

    def get_price_data(self, symbol: str) -> pd.DataFrame:
        """
        Hisse verisini Yahoo Finance üzerinden çeker.
        BIST hisseleri için '.IS' uzantısı eklenir.
        """

        if not symbol.endswith(".IS"):
            symbol = f"{symbol}.IS"

        df = yf.download(
            symbol,
            period=self.period,
            interval=self.interval,
            progress=False
        )

        if df.empty:
            return pd.DataFrame()

        df.dropna(inplace=True)
        return df

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Temel teknik indikatörleri hesaplar.
        """

        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()
        df["MA200"] = df["Close"].rolling(window=200).mean()

        df["RSI"] = self.calculate_rsi(df["Close"], 14)

        df["Volume_MA20"] = df["Volume"].rolling(window=20).mean()

        return df

    def calculate_rsi(self, series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
