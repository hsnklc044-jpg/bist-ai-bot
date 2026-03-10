from radar_engine import run_radar


def auto_scan():

    results = run_radar()

    alerts = []

    for symbol, score in results:

        if score > 80:

            alerts.append({
                "symbol": symbol,
                "score": score
            })

    return alerts