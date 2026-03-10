import yfinance as yf
import numpy as np

INDEX = "XU100.IS"


def analyze_market():

    try:

        data = yf.download(
            INDEX,
            period="3mo",
            interval="1d",
            progress=False
        )

        if data.empty:
            return "UNKNOWN", "UNKNOWN", "OFF"

        close = data["Close"].values.flatten()

        ma20 = np.mean(close[-20:])
        ma50 = np.mean(close[-50:])

        last = close[-1]

        if last > ma20 and ma20 > ma50:
            trend = "BULLISH"

        elif last < ma20 and ma20 < ma50:
            trend = "BEARISH"

        else:
            trend = "RANGE"

        volatility = np.std(close[-20:])

        if volatility < 50:
            risk = "LOW"
        elif volatility < 100:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        if trend == "BULLISH" and risk != "HIGH":
            mode = "ACTIVE"
        else:
            mode = "DEFENSIVE"

        return trend, risk, mode

    except:
        return "UNKNOWN", "UNKNOWN", "OFF"