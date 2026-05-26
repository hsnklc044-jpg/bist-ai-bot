import yfinance as yf
import pandas as pd


def get_support_resistance(symbol):

    try:

        df = yf.download(
            symbol,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):

            high = df["High"].iloc[:, 0]
            low = df["Low"].iloc[:, 0]
            close = df["Close"].iloc[:, 0]

        else:

            high = df["High"]
            low = df["Low"]
            close = df["Close"]

        price = round(
            float(close.iloc[-1]),
            2
        )

        # Yakın destekler

        support1 = round(
            float(low.tail(10).min()),
            2
        )

        support2 = round(
            float(low.tail(20).min()),
            2
        )

        # Yakın dirençler

        resistance1 = round(
            float(high.tail(10).max()),
            2
        )

        resistance2 = round(
            float(high.tail(20).max()),
            2
        )

        return {
            "symbol": symbol,
            "price": price,
            "support1": support1,
            "support2": support2,
            "resistance1": resistance1,
            "resistance2": resistance2
        }

    except Exception as e:

        print(f"[SR ERROR] {symbol}: {e}")

        return None