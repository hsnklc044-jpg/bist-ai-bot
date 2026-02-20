import pandas as pd
import yfinance as yf


class DataEngine:
    """
    BIST hisseleri için veri çekme ve teknik indikatör hesaplama motoru
    """

    def __init__(self):
        self.period = "2y"
        self.interval = "1d"

    def get_price_data(self, symbol: str) -> pd.DataFrame:

        if not symbol.endswith(".IS"):
            symbol = f"{symbol}.IS"

        df = yf.download(
            symbol,
            period=self.period,
            interval=self.interval,
            auto_adjust=True,
            progress=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        return df

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:

        if df is None or df.empty:
            return pd.DataFrame()

        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()
        df["MA200"] = df["Close"].rolling(window=200).mean()

        df["RSI"] = self._calculate_rsi(df["Close"])

        return df

    def _calculate_rsi(self, series: pd.Series, period: int = 14):

        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi
