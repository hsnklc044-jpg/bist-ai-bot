import yfinance as yf
import time


def get_data(ticker):

    try:

        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            print("⚠ Veri alınamadı:", ticker)
            return None

        time.sleep(1)

        return df

    except Exception as e:

        print("❌ Veri hatası:", ticker, e)

        return None
