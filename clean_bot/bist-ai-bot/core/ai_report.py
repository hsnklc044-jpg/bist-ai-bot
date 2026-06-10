from core.summary_report import generate_summary_report
from core.top_signals import get_top_signals

def generate_ai_report():

    signals = get_top_signals()

    if not signals:
        return "AI report oluşturulamadı."

    top = signals[0]

    message = (
        "🤖 QUANTBIST AI\n\n"
        "════════════════════\n\n"
        f"🔥 Best Signal\n"
        f"{top['symbol']}\n\n"
        f"⭐ Score\n"
        f"{top['score']}\n\n"
        f"📈 Trend\n"
        f"{top['trend']}\n\n"
        "════════════════════\n\n"
    )

    for i, s in enumerate(signals[:3], start=1):

        medal = ["🥇", "🥈", "🥉"][i-1]

        message += (
            f"{medal} {s['symbol']}\n"
            f"Score: {s['score']}\n\n"
        )

    return message