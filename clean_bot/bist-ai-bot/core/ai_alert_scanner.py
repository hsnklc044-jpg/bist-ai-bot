from core.top_signals import get_top_signals


def generate_ai_alerts():

    signals = get_top_signals()

    if not signals:
        return None

    report = "🚨 AI SIGNAL ALERT\n\n"

    count = 0

    for s in signals:

        if (
            s["score"] >= 70
            and s["trend"] == "BULLISH"
        ):

            report += (
                f"📈 {s['symbol']}\n"
                f"Signal : {s['signal']}\n"
                f"Score : {s['score']}\n"
                f"Trend : {s['trend']}\n\n"
            )

            count += 1

        if count >= 3:
            break

    if count == 0:

        return (
            "AI SIGNAL ALERT\n\n"
            "Bugun filtreleri gecen guclu sinyal bulunamadi."
        )

    return report