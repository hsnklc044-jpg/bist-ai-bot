import yfinance as yf
import pandas as pd
import asyncio
from telegram import Bot

TOKEN = "8434925197:AAEzOTp4Q0zjRSlcHjQg8Mj9tvagXZHN1uI"
CHAT_ID = "1790584407"

bot = Bot(token=TOKEN)

symbols = [
    "EREGL","THYAO","SASA","ASELS","KRDMD","ISCTR","GARAN","AKBNK",
    "YKBNK","SISE","PETKM","TUPRS","HEKTS","BIMAS","FROTO"
]

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
# AI YORUM
# ================================
def generate_ai_comment(price, support, resistance, ema, rsi, rr):

    comments = []

    if price > ema:
        comments.append("Trend güçlü ↑")
    else:
        comments.append("Trend zayıf ↓")

    if abs(price - resistance)/price < 0.02:
        comments.append("Dirence çok yakın")

    if rsi > 60:
        comments.append("Momentum güçlü")

    if rr >= 2:
        decision = "İŞLEM AL ✅"
    elif rr >= 1.5:
        decision = "TAKİP ET 👀"
    else:
        decision = "UZAK DUR ❌"

    return "\n".join(comments), decision

# ================================
# SİNYAL MOTORU
# ================================
def check_signal(df):

    df['EMA'] = calculate_ema(df)
    df['RSI'] = calculate_rsi(df)

    try:
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        rsi = df['RSI'].iloc[-1]
        rsi_prev = df['RSI'].iloc[-2]
        ema = df['EMA'].iloc[-1]
    except:
        return None

    support = df['Low'].rolling(20).min().iloc[-1]
    resistance = df['High'].rolling(20).max().iloc[-1]
    atr = calculate_atr(df)

    distance = (resistance - price) / price

    # BREAKOUT
    if price > resistance and prev_price <= resistance and price > ema and rsi > 55:
        rr = 2
        return "🚀 BREAKOUT", price, price+atr*2, price-atr, rr, support, resistance, ema, rsi

    # YAKLAŞAN
    if price > ema and rsi > 55 and rsi > rsi_prev and distance < 0.03:
        rr = round((resistance - price)/atr,2)
        return "⚡ YAKLAŞAN BREAKOUT", price, resistance, price-atr, rr, support, resistance, ema, rsi

    return None

# ================================
# ANA LOOP
# ================================
async def run():

    print("🚀 AI SCANNER AKTİF")

    while True:

        for symbol in symbols:

            try:
                df = get_data(symbol)

                if df is None:
                    continue

                result = check_signal(df)

                if result:

                    signal, entry, target, stop, rr, support, resistance, ema, rsi = result

                    if rr < 1.3:
                        continue

                    comment, decision = generate_ai_comment(
                        entry, support, resistance, ema, rsi, rr
                    )

                    msg = (
                        f"🚨 AKILLI FIRSAT\n\n"
                        f"📊 {symbol}\n"
                        f"{signal}\n\n"
                        f"Giriş: {entry:.2f}\n"
                        f"TP: {target:.2f}\n"
                        f"SL: {stop:.2f}\n"
                        f"RR: {rr}\n\n"
                        f"🧠 Yorum:\n{comment}\n\n"
                        f"🚦 Karar: {decision}"
                    )

                    await bot.send_message(CHAT_ID, msg)

            except Exception as e:
                print(symbol, "hata:", e)

        await asyncio.sleep(600)

# ================================
# START
# ================================
if __name__ == "__main__":
    asyncio.run(run())