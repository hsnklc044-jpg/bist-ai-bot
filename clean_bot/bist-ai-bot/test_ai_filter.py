from core.ai_filter import AIFilter
from tg.notifier import TelegramNotifier

symbols = [
    "EREGL.IS",
    "THYAO.IS",
    "SISE.IS",
    "TUPRS.IS",
    "ASELS.IS"
]

ai = AIFilter()

telegram = TelegramNotifier(
    token="8434925197:AAHeciNObLAkLJ_SE_jsaNPvhiwR9_HRoTE",
    chat_id="1790584407"
)

for symbol in symbols:

    result = ai.analyze(symbol)

    print("\n====================")
    print(result)

    if result and result["signal"]:

        message = f"""
🤖 AI FILTER SIGNAL

Symbol: {result['symbol']}

Signal: {result['signal']}

AI Score: {result['score']}

Trend: {result['trend']}

Volatility: {result['volatility']}

Volume Ratio: {result['volume_ratio']}
"""

        telegram.send(message)

        print("[TELEGRAM] AI Signal Sent")