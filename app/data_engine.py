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

        return df
