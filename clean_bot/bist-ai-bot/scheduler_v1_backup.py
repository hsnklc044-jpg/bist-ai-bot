import time
import schedule
import asyncio

from telegram import Bot

from core.morning_report import (
    generate_morning_report
)

BOT_TOKEN = "8434925197:AAHeciNObLAkLJ_SE_jsaNPvhiwR9_HRoTE"
CHAT_ID = 1790584407


async def send_morning_report():

    bot = Bot(BOT_TOKEN)

    report = generate_morning_report()

    await bot.send_message(
        chat_id=CHAT_ID,
        text=report
    )

    print(
        "Morning report sent."
    )


def run_report():

    asyncio.run(
        send_morning_report()
    )


schedule.every().day.at(
    "09:00"
).do(
    run_report
)

print(
    "QuantBIST Scheduler Started..."
)

while True:

    schedule.run_pending()

    time.sleep(30)