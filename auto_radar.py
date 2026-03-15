import time
import telebot
from bist100_engine import scan_bist100

TOKEN = "8772282578:AAHayduiZtDuf659L0Fx9H8ehOcn81tii10"
CHAT_ID = "1790584407"

bot = telebot.TeleBot(TOKEN)


def run_radar():

    while True:

        try:

            results = scan_bist100()

            strong = []

            for r in results:

                if r[1] >= 70:
                    strong.append(r)

            if len(strong) > 0:

                message = "🚨 BIST AI RADAR\n\n"

                for s in strong:

                    message += f"{s[0]} | Score: {s[1]}\n"

                bot.send_message(CHAT_ID, message)

        except Exception as e:

            print("Radar hata:", e)

        time.sleep(300)
