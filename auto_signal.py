from breakout_engine import breakout_scan

def check_signals():

    signals = breakout_scan()

    alerts = []

    for s in signals:

        text = f"""
🚨 BREAKOUT ALERT

Hisse: {s[0]}
Fiyat: {s[1]}
Volume Spike: {s[2]}x
"""

        alerts.append(text)

    return alerts