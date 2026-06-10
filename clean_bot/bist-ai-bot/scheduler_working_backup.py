import time
import schedule
import asyncio

from telegram import Bot

from core.ai_alert_scanner import generate_ai_alerts
from core.morning_report import generate_morning_report
from core.end_of_day_report import generate_end_of_day_report

from config import BOT_TOKEN, CHAT_ID


async def send_morning_report():

    bot = Bot(BOT_TOKEN)

    report = generate_morning_report()

    await bot.send_message(
        chat_id=CHAT_ID,
        text=report
    )

    print("Morning report sent.")


async def send_ai_alerts():

    bot = Bot(BOT_TOKEN)

    report = generate_ai_alerts()

    if report:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=report
        )

        print("AI alerts sent.")

    else:

        print("No AI alerts.")


async def send_eod_report():

    bot = Bot(BOT_TOKEN)

    report = generate_end_of_day_report()

    await bot.send_message(
        chat_id=CHAT_ID,
        text=report
    )

    print("End of day report sent.")


def run_morning():

    asyncio.run(send_morning_report())


def run_ai_alerts():

    asyncio.run(send_ai_alerts())


def run_eod():

    asyncio.run(send_eod_report())


schedule.every().day.at("09:00").do(run_morning)
schedule.every().day.at("09:15").do(run_ai_alerts)
schedule.every().day.at("18:10").do(run_eod)

print("QuantBIST Scheduler V3 Started...")

while True:

    schedule.run_pending()

    time.sleep(30)