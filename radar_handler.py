from telegram import Update
from telegram.ext import ContextTypes
import os
import pandas as pd

from signal_engine import radar_scan


DATA_FOLDER = "data"


def load_data():

    data = {}

    for file in os.listdir(DATA_FOLDER):

        if file.endswith(".csv"):

            symbol = file.replace(".csv","")

            df = pd.read_csv(os.path.join(DATA_FOLDER,file))

            df["Date"] = pd.to_datetime(df["Date"])

            df.set_index("Date", inplace=True)

            data[symbol] = df

    return data


async def radar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📡 Radar taraması yapılıyor...")

    data = load_data()

    results = radar_scan(data)

    message = "🔥 BIST RADAR\n\n"

    top = results[:10]

    for i,(symbol,score) in enumerate(top,1):

        message += f"{i}. {symbol}  |  Score: {score}\n"

    await update.message.reply_text(message)
