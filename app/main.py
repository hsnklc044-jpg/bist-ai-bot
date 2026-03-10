import logging
import asyncio

from scanner import run_scanner
from telegram_sender import send_telegram_message


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def radar():

    print("Radar çalışıyor...")

    results = run_scanner()

    message = "📡 BIST AI RADAR\n\n"

    for i, r in enumerate(results[:10], 1):

        symbol = r["symbol"]
        score = r["score"]

        message += f"{i}. {symbol}  |  Score: {score}\n"

    await send_telegram_message(message)


async def main():

    print("Bot başlatıldı")

    await radar()


if __name__ == "__main__":

    asyncio.run(main())
