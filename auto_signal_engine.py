import time
from ai_trade_engine import ai_trade_signals


def run_auto_signals(bot, chat_id):

    sent_signals = set()

    while True:

        try:

            signals = ai_trade_signals()

            if signals:

                for stock, score in signals:

                    key = f"{stock}-{score}"

                    if key not in sent_signals:

                        text = f"""
🚨 AI TRADE SIGNAL

Hisse: {stock}
AI Score: {score}

Trend + Volume + Breakout uyumu
"""

                        bot.send_message(chat_id, text)

                        sent_signals.add(key)

            time.sleep(300)

        except Exception as e:

            print("Auto signal hata:", e)

            time.sleep(60)