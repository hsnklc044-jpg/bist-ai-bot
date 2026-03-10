from radar_engine import run_radar
from trade_engine import get_trade_setup


def check_alerts():

    radar = run_radar()

    alerts = []

    for symbol, score in radar:

        try:

            # güçlü AI sinyali
            if score < 80:
                continue

            trade = get_trade_setup(symbol)

            if trade is None:
                continue

            entry, stop, target, rr = trade

            # risk reward filtresi
            if rr < 2:
                continue

            alerts.append({
                "symbol": symbol,
                "score": score,
                "entry": round(entry, 2),
                "stop": round(stop, 2),
                "target": round(target, 2),
                "rr": round(rr, 2)
            })

        except Exception as e:

            print(f"Alert engine error for {symbol}: {e}")
            continue

    return alerts