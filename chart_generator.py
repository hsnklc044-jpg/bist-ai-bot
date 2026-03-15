import yfinance as yf
import pandas as pd


def get_chart(symbol):

    try:

        df = yf.download(symbol, period="3mo", progress=False)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"]

        if len(close) < 20:
            return ""

        start = close.iloc[0]
        end = close.iloc[-1]

        change = (end/start - 1) * 100

        if change > 5:
            return "📈 Strong Uptrend"

        elif change > 0:
            return "📈 Uptrend"

        elif change > -5:
            return "➡️ Sideways"

        else:
            return "📉 Downtrend"

    except:

        return ""
