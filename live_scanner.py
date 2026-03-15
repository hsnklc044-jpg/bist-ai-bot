from radar_engine import run_radar
from decision_engine import get_trade_decision


def scan_market():

    signals = []

    radar = run_radar()

    for symbol, score in radar:

        try:

            decision = get_trade_decision(symbol)

            if decision is None:
                continue

            if decision["action"] == "BUY":

                signals.append({
                    "symbol": symbol,
                    "score": decision["score"],
                    "trend": decision["trend"],
                    "action": decision["action"]
                })

        except:

            continue

    return signals[:5]
