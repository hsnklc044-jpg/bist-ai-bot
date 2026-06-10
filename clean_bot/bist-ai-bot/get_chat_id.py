from telegram import Bot
import asyncio

TOKEN = "8434925197:AAHeciNObLAkLJ_SE_jsaNPvhiwR9_HRoTE"

async def main():

    bot = Bot(TOKEN)

    updates = await bot.get_updates()

    for u in updates:
        print(u)

asyncio.run(main())