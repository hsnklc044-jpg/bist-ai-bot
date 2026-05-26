# ================================
# TEST (DOĞRU DOSYA MI?)
# ================================
print("✅ BOT V2 CALISIYOR")

# ================================
# MATPLOTLIB FIX
# ================================
import matplotlib
matplotlib.use('Agg')

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8434925197:AAEzOTp4Q0zjRSlcHjQg8Mj9tvagXZHN1uI"

ACCOUNT_SIZE = 100000
RISK_PERCENT = 0.02

# ================================
# VERİ
# ================================
def get_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="3mo", interval="1d", progress=False)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[['Open','High','Low','Close','Volume']].dropna()

        if len(df) < 50:
            return None

        return df

    except:
        return None

# ================================
# RSI
# ================================
def calculate_rsi(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================================
# EMA
# ================================
def calculate_ema(df):
    return df['Close'].ewm(span=200).mean()

# ================================
# ATR
# ================================
def calculate_atr(df):
    tr = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - df['Close'].shift()).abs(),
        (df['Low'] - df['Close'].shift()).abs()
    ], axis=1).max(axis=1)

    return tr.rolling(14).mean().iloc[-1]

# ================================
# DESTEK DİRENÇ
# ================================
def calculate_sr(df):
    support = float(df['Low'].rolling(20).min().iloc[-1])
    resistance = float(df['High'].rolling(20).max().iloc[-1])
    return support, resistance

# ================================
# RR
# ================================
def calculate_rr(entry, target, stop, signal_type):
    try:
        if signal_type == "AL":
            return round((target - entry) / (entry - stop), 2)
        else:
            return round((entry - target) / (stop - entry), 2)
    except:
        return 0

# ================================
# POZİSYON
# ================================
def calculate_position(entry, stop):
    risk_amount = ACCOUNT_SIZE * RISK_PERCENT
    risk_per_share = abs(entry - stop)

    if risk_per_share == 0:
        return 0, 0

    qty = risk_amount / risk_per_share
    size = qty * entry

    return int(qty), int(size)

# ================================
# AI YORUM + KARAR
# ================================
def generate_comment(price, support, resistance, ema, rsi, rr):

    comments = []

    if price > ema:
        comments.append("Trend yukarı")
    else:
        comments.append("Trend aşağı")

    if abs(price - resistance)/price < 0.02:
        comments.append("Dirence yakın")
    elif abs(price - support)/price < 0.02:
        comments.append("Desteğe yakın")

    if rsi > 60:
        comments.append("Momentum güçlü")
    elif rsi < 40:
        comments.append("Momentum zayıf")

    if rr >= 2:
        decision = "İŞLEM AL ✅"
    elif rr >= 1.5:
        decision = "DİKKATLİ ⚠️"
    else:
        decision = "İŞLEM ALMA ❌"

    return "\n".join(comments), decision

# ================================
# SİNYAL
# ================================
def generate_signal(df):

    if df is None or len(df) < 50:
        return None

    df['EMA'] = calculate_ema(df)
    df['RSI'] = calculate_rsi(df)

    try:
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        rsi = df['RSI'].iloc[-1]
        ema = df['EMA'].iloc[-1]
    except:
        return None

    support, resistance = calculate_sr(df)
    atr = calculate_atr(df)

    buy = support
    sell = resistance

    buy_stop = buy - atr
    sell_stop = sell + atr

    buy_target = resistance
    sell_target = support

    signal = "BEKLE"
    rr = 0

    # 🚀 BREAKOUT AL
    if price > resistance and prev_price <= resistance and price > ema and rsi > 55:
        signal = "🚀 BREAKOUT AL"
        buy = price
        buy_target = price + atr * 2
        buy_stop = price - atr
        rr = calculate_rr(buy, buy_target, buy_stop, "AL")

    return signal, buy, sell, buy_target, buy_stop, sell_target, sell_stop, ema, rsi, atr, rr, support, resistance

# ================================
# GRAFİK
# ================================
def plot_chart(df, support, resistance, symbol):
    plt.style.use('dark_background')
    plt.figure(figsize=(12,6))

    plt.plot(df['Close'].values)
    plt.plot(df['EMA'].values, linestyle='--')

    plt.axhline(support, color='green')
    plt.axhline(resistance, color='red')

    plt.title(symbol)
    plt.grid(alpha=0.3)

    plt.savefig("chart.png")
    plt.close()

# ================================
# KOMUT
# ================================
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = context.args[0].upper()

    await update.message.reply_text(f"{symbol} analiz ediliyor...")

    df = get_data(symbol)

    if df is None:
        await update.message.reply_text("❌ Veri alınamadı")
        return

    result = generate_signal(df)

    if result is None:
        await update.message.reply_text("❌ Veri yetersiz")
        return

    signal, buy, sell, bt, bs, st, ss, ema, rsi, atr, rr, support_val, resistance_val = result

    plot_chart(df, support_val, resistance_val, symbol)

    # 🔥 YORUM + KARAR
    comment, decision = generate_comment(
        df['Close'].iloc[-1],
        support_val,
        resistance_val,
        ema,
        rsi,
        rr
    )

    # 💰 POZİSYON
    if "AL" in signal:
        qty, pos = calculate_position(buy, bs)
    else:
        qty, pos = 0, 0

    msg = (
        f"📊 {symbol}\n\n"
        f"📉 EMA200: {ema:.2f}\n"
        f"📏 ATR: {atr:.2f}\n"
        f"📊 RSI: {rsi:.2f}\n\n"
        f"🟢 AL: {buy:.2f} | 🎯 {bt:.2f} | 🛑 {bs:.2f}\n"
        f"🔴 SAT: {sell:.2f} | 🎯 {st:.2f} | 🛑 {ss:.2f}\n\n"
        f"🚀 Sinyal: {signal}\n"
        f"📊 RR: {rr}\n\n"
        f"🧠 Yorum:\n{comment}\n\n"
        f"🚦 Karar: {decision}\n\n"
        f"💰 Pozisyon:\nLot: {qty}\nTutar: {pos} TL"
    )

    with open("chart.png", "rb") as photo:
        await update.message.reply_photo(photo=photo, caption=msg)

# ================================
# MAIN
# ================================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("support", support))

    print("🚀 BOT V2 AKTİF")
    app.run_polling()

if __name__ == "__main__":
    main()