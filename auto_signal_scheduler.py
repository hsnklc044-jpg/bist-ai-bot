import asyncio
from scanner_ai import scan_market


async def auto_signal_loop(app):

    while True:

        results = scan_market()

        if results:

            msg = "🚨 AI TRADE ALERT\n\n"

            msg += "\n".join(results[:5])

            for chat_id in app.bot_data.get("subscribers", []):

                try:
                    await app.bot.send_message(chat_id=chat_id, text=msg)
                except:
                    pass

        await asyncio.sleep(1800)  # 30 dakika