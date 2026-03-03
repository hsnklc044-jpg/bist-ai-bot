import os
import logging
import psycopg2
import numpy as np
import io
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# ================= DB =================

def get_connection():
    url = urlparse(DATABASE_URL)
    return psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname=url.path[1:]
    )

# ================= INDICATORS =================

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= TAM BIST LİSTESİ (İlk 200 Aktif Hisse) =================

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

# ================= SCOUT PRO =================

async def bebek(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🚀 TAM BIST PRO tarıyor...")

    candidates = []

    for symbol in BIST_SYMBOLS:

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if len(df) < 30:
                continue

            df["RSI"] = compute_rsi(df["Close"], 14)
            df["EMA20"] = df["Close"].ewm(span=20).mean()
            df["Mom5"] = df["Close"].pct_change(5) * 100
            df["VolAvg20"] = df["Volume"].rolling(20).mean()

            last = df.iloc[-1]

            # PROFESYONEL SKORLAMA
            trend = 1 if last["Close"] > last["EMA20"] else 0
            momentum = last["Mom5"]
            volume_score = last["Volume"] / last["VolAvg20"] if last["VolAvg20"] != 0 else 0
            rsi_score = last["RSI"]

            score = (momentum * 0.4) + (volume_score * 20 * 0.3) + (rsi_score * 0.3)

            if trend == 1 and momentum > 1:

                entry = last["Close"]
                stop = df["Low"].rolling(5).min().iloc[-1]
                risk = entry - stop
                target = entry + risk * 2

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
        return await update.message.reply_text("❌ Güçlü momentum yok.")

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:10]

    message = "🔥 TAM BIST MOMENTUM LİSTESİ\n\n"

    for c in candidates:
        message += (
            f"{c['symbol']} | Entry:{c['entry']} | Stop:{c['stop']} | Target:{c['target']}\n"
        )

    await update.message.reply_text(message)

# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("bebek", bebek))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
