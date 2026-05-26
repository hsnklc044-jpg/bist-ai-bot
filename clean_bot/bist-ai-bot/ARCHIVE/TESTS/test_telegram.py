import asyncio
from telegram import Bot

TOKEN = "8434925197:AAEzOTp4Q0zjRSlcHjQg8Mj9tvagXZHN1uI"
CHAT_ID = 1790584407

async def main():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="🔥 TEST MESAJI GELDİ")

asyncio.run(main())