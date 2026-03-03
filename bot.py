import os
import logging
import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")

# ================= BIST SYMBOLS =================

BIST_SYMBOLS = [
    "AEFES.IS","AKBNK.IS","AKSA.IS","AKSEN.IS","ALARK.IS","ALBRK.IS","ALFAS.IS",
    "ANSGR.IS","ARCLK.IS","ASELS.IS","ASTOR.IS","BIMAS.IS","BRLSM.IS","CANTE.IS",
    "CCOLA.IS","CIMSA.IS","CWENE.IS","DOHOL.IS","EGEEN.IS","EKGYO.IS","ENJSA.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GESAN.IS","GLYHO.IS","GUBRF.IS",
    "HEKTS.IS","ISCTR.IS","ISDMR.IS","KARSN.IS","KCHOL.IS","KONTR.IS","KORDS.IS",
    "KRDMD.IS","KOZAA.IS","KOZAL.IS","LOGO.IS","MGROS.IS","MIATK.IS","ODAS.IS",
    "OYAKC.IS","PETKM.IS","PGSUS.IS","PSGYO.IS","SAHOL.IS","SASA.IS","SMRTG.IS",
    "TAVHL.IS","TCELL.IS","THYAO.IS","TKFEN.IS","TOASO.IS","TSKB.IS","TUPRS.IS",
    "ULKER.IS","VAKBN.IS","YKBNK.IS","ZOREN.IS"
]

# ================= RSI =================

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= RELATIVE STRENGTH ENGINE =================

async def bebek(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🔥 RS PRO tarıyor...")

    try:
        tickers = BIST_SYMBOLS + ["XU100.IS"]

        data = yf.download(
            tickers=" ".join(tickers),
            period="3mo",
            interval="1d",
            group_by="ticker",
            progress=False
        )
    except:
        return await update.message.reply_text("Veri çekilemedi.")

    try:
        index_df = data["XU100.IS"].dropna()
        index_return = (index_df["Close"].iloc[-1] / index_df["Close"].iloc[-20]) - 1
    except:
        return await update.message.reply_text("Endeks verisi alınamadı.")

    candidates = []

    for symbol in BIST_SYMBOLS:

        try:
            df = data[symbol].dropna()

            if len(df) < 30:
                continue

            df["EMA20"] = df["Close"].ewm(span=20).mean()
            df["RSI"] = compute_rsi(df["Close"], 14)

            stock_return = (df["Close"].iloc[-1] / df["Close"].iloc[-20]) - 1
            relative_strength = stock_return - index_return

            last = df.iloc[-1]

            cond_trend = last["Close"] > last["EMA20"]
            cond_rs = relative_strength > 0
            cond_rsi = last["RSI"] > 50

            if cond_trend and cond_rs and cond_rsi:

                entry = last["Close"]
                stop = df["Low"].rolling(5).min().iloc[-1]
                risk = entry - stop
                target = entry + risk * 2

                score = relative_strength * 100

                candidates.append({
                    "symbol": symbol.replace(".IS",""),
                    "entry": round(entry,2),
                    "stop": round(stop,2),
                    "target": round(target,2),
                    "score": score
                })

        except:
            continue

    if not candidates:
        return await update.message.reply_text("❌ Endeksten güçlü hisse yok.")

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:10]

    message = "🔥 RELATIVE STRENGTH LİDERLERİ\n\n"

    for c in candidates:
        message += (
            f"{c['symbol']} | Entry:{c['entry']} | "
            f"Stop:{c['stop']} | Target:{c['target']}\n"
        )

    await update.message.reply_text(message)

# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("bebek", bebek))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
