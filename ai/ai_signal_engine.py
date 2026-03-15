from radar_engine import run_radar

def get_signal():

    results = run_radar()

    if not results:
        return "Sinyal bulunamadı."

    best = results[0]

    symbol = best[0]
    score = best[1]

    if score >= 8:
        risk = "Düşük"
    elif score >= 6:
        risk = "Orta"
    else:
        risk = "Yüksek"

    msg = f"""
🚨 AI Breakout

Hisse: {symbol}
Skor: {score}/10
Risk: {risk}
"""

    return msg
