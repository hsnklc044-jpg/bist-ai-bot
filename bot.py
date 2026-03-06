import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from engine.ultimate_scanner import run_ultimate_scanner
from engine.support_resistance_engine import get_support_resistance
from engine.heatmap_engine import get_heatmap


TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = (

        "🤖 BIST AI Radar Bot\n\n"
        "Komutlar:\n"
        "/radar → Günün radar sinyalleri\n"
        "/support ASELS → Destek / Direnç\n"
        "/heatmap → Günün en güçlü hisseleri"

    )

    await update.message.reply_text(message)


async def radar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📡 Radar çalışıyor...")

    results = run_ultimate_scanner()

    if not results:

        await update.message.reply_text("Sinyal bulunamadı")

        return

    for r in results:

        await update.message.reply_text(r)


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        symbol = context.args[0].upper()

        data = get_support_resistance(symbol)

        if data is None:

            await update.message.reply_text("Hisse bulunamadı")

            return

        message = (

            f"📊 {symbol}\n\n"
            f"Fiyat: {data['price']}\n"
            f"Destek: {data['support']}\n"
            f"Direnç: {data['resistance']}"

        )

        await update.message.reply_text(message)

    except:

        await update.message.reply_text("Kullanım: /support ASELS")


async def heatmap(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🔥 Heatmap hazırlanıyor...")

    signals = get_heatmap()

    if not signals:

        await update.message.reply_text("Heatmap oluşturulamadı")

        return

    message = "🔥 Günün En Güçlü Hisseleri\n\n"

    for i, s in enumerate(signals, 1):

        message += f"{i}️⃣ {s}\n\n"

    await update.message.reply_text(message)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("radar", radar))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("heatmap", heatmap))

    print("🤖 Telegram bot çalışıyor...")

    app.run_polling()


if __name__ == "__main__":

    main()
