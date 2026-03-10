from radar_engine import run_radar
from forecast_engine import forecast_trend
import yfinance as yf


def generate_trade_setups():

    radar = run_radar()

    if not radar:
        return []

    setups = []

    for symbol, score in radar[:5]:

        try:

            forecast = forecast_trend(symbol)

            if forecast is None:
                continue

            df = yf.Ticker(symbol + ".IS").history(period="1mo")

            price = float(df["Close"].iloc[-1])

            entry = price
            stop = price * 0.95
            target = price * 1.10

            confidence = int((score + forecast["confidence"]) / 2)

            setups.append({
                "symbol": symbol,
                "entry": round(entry,2),
                "stop": round(stop,2),
                "target": round(target,2),
                "confidence": confidence
            })

        except:
            continue

    return setups