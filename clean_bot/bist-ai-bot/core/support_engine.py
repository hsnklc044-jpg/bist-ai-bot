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

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):

            close = df["Close"].iloc[:, 0]
            high = df["High"].iloc[:, 0]
            low = df["Low"].iloc[:, 0]

        else:

            close = df["Close"]
            high = df["High"]
            low = df["Low"]

        # NaN temizliği

        price_df = pd.DataFrame({
            "close": close,
            "high": high,
            "low": low
        }).dropna()

        if price_df.empty:
            return None

        close = price_df["close"]
        high = price_df["high"]
        low = price_df["low"]

        current_price = round(
            float(close.iloc[-1]),
            2
        )

        support_1 = round(
            float(low.tail(20).min()),
            2
        )

        support_2 = round(
            float(low.tail(50).min()),
            2
        )

        resistance_1 = round(
            float(high.tail(20).max()),
            2
        )

        resistance_2 = round(
            float(high.tail(50).max()),
            2
        )

        ma20 = float(
            close.rolling(20).mean().iloc[-1]
        )

        ma50 = float(
            close.rolling(50).mean().iloc[-1]
        )

        trend = (
            "BULLISH"
            if ma20 > ma50
            else "BEARISH"
        )

        return {

            "symbol": symbol,

            "price": current_price,

            "support_1": support_1,
            "support_2": support_2,

            "resistance_1": resistance_1,
            "resistance_2": resistance_2,

            "trend": trend
        }

    except Exception as e:

        print(
            f"[SUPPORT ERROR] "
            f"{symbol}: {e}"
        )

        return None