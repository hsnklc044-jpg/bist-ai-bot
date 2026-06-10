from telegram import Bot
import asyncio

from core.morning_report import (
    generate_morning_report
)

BOT_TOKEN = "8434925197:AAHeciNObLAkLJ_SE_jsaNPvhiwR9_HRoTE"
CHAT_ID = 1790584407


async def send_report():

    bot = Bot(BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=generate_morning_report()
    )


asyncio.run(
    send_report()
)