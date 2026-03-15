from ai_signal_engine import get_signal
from radar_engine import run_radar

last_signal = None

def run_scheduler(bot, chat_id):

    global last_signal

    results = run_radar()

    if not results:
        return

    best = results[0]

    symbol = best[0]
    score = best[1]

    if score < 8:
        return

    signal = f"{symbol}-{score}"

    if signal == last_signal:
        return

    last_signal = signal

    msg = f"""
🚨 AI Radar Alert

Hisse: {symbol}
Skor: {score}/10
Trend: Güçlü
"""

    bot.send_message(chat_id=chat_id, text=msg)
