import yfinance as yf
import pandas as pd


def analyze_market():

    try:

        df = yf.download("XU100.IS", period="6mo", interval="1d", progress=False)

        if df.empty:
            return {
                "trend": "Unknown",
                "momentum": "Unknown",
                "risk": "Unknown"
            }

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"]

        ma50 = close.rolling(50).mean().iloc[-1]
        ma200 = close.rolling(200).mean().iloc[-1]

        current = close.iloc[-1]

        # Trend
        if current > ma50 > ma200:
            trend = "Bullish 🟢"

        elif current < ma50 < ma200:
            trend = "Bearish 🔴"

        else:
            trend = "Sideways 🟡"

        # Momentum
        momentum = (current / close.iloc[-20] - 1) * 100

        if momentum > 5:
            momentum_status = "Strong"

        elif momentum > 0:
            momentum_status = "Positive"

        else:
            momentum_status = "Weak"

        # Risk (volatilite)
        volatility = close.pct_change().std() * 100

        if volatility > 2:
            risk = "High"

        elif volatility > 1:
            risk = "Medium"

        else:
            risk = "Low"

        return {
            "trend": trend,
            "momentum": momentum_status,
            "risk": risk
        }

    except Exception as e:

        print("MARKET ANALYZER HATA:", e)

        return {
            "trend": "Unknown",
            "momentum": "Unknown",
            "risk": "Unknown"
        }
