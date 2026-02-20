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
        """
        Yahoo Finance üzerinden BIST hisse verisini çeker.
        Örnek: ASELS -> ASELS.IS
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
        Teknik indikatörleri hesaplar:
        - MA20
        - MA50
        - MA200
        - RSI
        - Hacim Ortalaması
        """

        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()
        df["MA200"] = df["Close"].rolling(window=200).mean()

        df["RSI"] = self.calculate_rsi(df["Close"], 14)

        df["Volume_MA20"] = df["Volume"].rolling(window=20).mean()

        return df

    def calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """
        RSI hesaplama fonksiyonu
        """

        delta = series.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi
