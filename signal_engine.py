from radar_engine import run_radar
from ai_engine import get_ai_score
from forecast_engine import forecast_trend


def generate_trade_signals():

    radar = run_radar()

    if not radar:
        return []

    signals = []

    for symbol, score in radar[:10]:

        try:

            ai_score = get_ai_score(symbol)

            forecast = forecast_trend(symbol)

            if ai_score is None or forecast is None:
                continue

            confidence = int((ai_score + forecast["confidence"]) / 2)

            if confidence < 70:
                continue

            entry = forecast["move"]

            signals.append({
                "symbol": symbol,
                "confidence": confidence,
                "move": forecast["move"]
            })

        except:
            continue

    return signals