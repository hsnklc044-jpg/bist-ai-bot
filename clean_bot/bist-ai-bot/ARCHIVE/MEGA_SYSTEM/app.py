import os
import requests
import numpy as np
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==============================
# CONFIG
# ==============================
TOKEN = os.getenv("BOT_TOKEN")  # Railway env'e ekle
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app.up.railway.app

app = Flask(__name__)

# ==============================
# DATA FUNCTIONS
# ==============================

def get_stock_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.IS"
        r = requests.get(url).json()
        price = r["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return price
    except:
        return None


def get_historical_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.IS?range=1mo&interval=1d"
        r = requests.get(url).json()
        closes = r["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        return [c for c in closes if c is not None]
    except:
        return []


def calculate_support(prices):
    if len(prices) < 5:
        return None

    # basit destek: en düşük %20 dilim ortalaması
    prices_sorted = sorted(prices)
    n = max(1, int(len(prices) * 0.2))
    support = np.mean(prices_sorted[:n])
    return round(support, 2)


# ==============================
# COMMANDS
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 BIST AI Bot aktif!\n\n"
        "Komutlar:\n"
        "/price EREGL\n"
        "/support EREGL"
    )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Hisse gir: /price EREGL")
        return

    symbol = context.args[0].upper()
    price = get_stock_price(symbol)

    if price:
        await update.message.reply_text(f"💰 {symbol} fiyat: {price} TL")
    else:
        await update.message.reply_text("Veri alınamadı.")


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Hisse gir: /support EREGL")
        return

    symbol = context.args[0].upper()
    prices = get_historical_data(symbol)

    if not prices:
        await update.message.reply_text("Veri alınamadı.")
        return

    support_level = calculate_support(prices)

    if support_level:
        await update.message.reply_text(
            f"📉 {symbol} destek seviyesi: {support_level} TL"
        )
    else:
        await update.message.reply_text("Hesaplanamadı.")


# ==============================
# TELEGRAM SETUP
# ==============================

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("price", price))
application.add_handler(CommandHandler("support", support))


# ==============================
# WEBHOOK ROUTES
# ==============================

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"


@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"


# ==============================
# STARTUP
# ==============================

@app.before_first_request
def setup():
    application.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)