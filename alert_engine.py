from breakout_scanner import breakout_scan


def generate_alert():

    results = breakout_scan()

    alerts = []

    for r in results:

        alerts.append(
            f"🚨 BREAKOUT ALERT\n\n{r} breakout detected"
        )

    return alerts