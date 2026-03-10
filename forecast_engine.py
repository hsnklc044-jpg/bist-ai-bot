import yfinance as yf
import numpy as np


def forecast_trend(symbol):

    try:

        ticker = yf.Ticker(symbol + ".IS")

        df = ticker.history(period="6mo")

        if df.empty or len(df) < 60:
            return None

        closes = df["Close"].values

        # basit regresyon trend
        x = np.arange(len(closes))
        slope = np.polyfit(x, closes, 1)[0]

        price = float(closes[-1])

        volatility = np.std(closes[-20:]) / price * 100

        if slope > 0:
            trend = "Bullish"
        else:
            trend = "Bearish"

        expected_move = round(volatility * 2, 2)

        confidence = min(90, int(abs(slope) * 1000))

        horizon = 3

        return {
            "symbol": symbol,
            "trend": trend,
            "move": expected_move,
            "confidence": confidence,
            "horizon": horizon
        }

    except:

        return None