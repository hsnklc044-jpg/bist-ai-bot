from telegram import Bot
import asyncio

TOKEN = "8434925197:AAHeciNObLAkLJ_SE_jsaNPvhiwR9_HRoTE"

async def test():
    bot = Bot(TOKEN)
    me = await bot.get_me()
    print(me)

asyncio.run(test())