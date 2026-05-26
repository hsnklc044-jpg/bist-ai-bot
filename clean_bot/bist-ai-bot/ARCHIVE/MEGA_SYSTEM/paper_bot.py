# ================================
# MATPLOTLIB FIX
# ================================
import matplotlib
matplotlib.use('Agg')

import yfinance as yf
import pandas as pd
import asyncio
from telegram import Bot

TOKEN = "8434925197:AAEzOTp4Q0zjRSlcHjQg8Mj9tvagXZHN1uI"
CHAT_ID = "1790584407"

bot = Bot(token=TOKEN)

# ================================
# AYARLAR
# ================================
symbols = ["EREGL", "THYAO", "SASA", "ASELS"]
balance = 100000

open_trades = []

# ================================
# VERİ
# ================================
def get_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="3mo", interval="1h", progress=False)

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
# SİNYAL
# ================================
def generate_signal(df):

    if df is None or len(df) < 50:
        return None, None, None, None

    df['EMA'] = calculate_ema(df)
    df['RSI'] = calculate_rsi(df)

    try:
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        rsi = df['RSI'].iloc[-1]
        rsi_prev = df['RSI'].iloc[-2]
        ema = df['EMA'].iloc[-1]
    except:
        return None, None, None, None

    support = df['Low'].rolling(20).min().iloc[-1]
    resistance = df['High'].rolling(20).max().iloc[-1]
    atr = calculate_atr(df)

    # 🚀 BREAKOUT AL
    if price > resistance and prev_price <= resistance and price > ema and rsi > 55:
        return "AL", price, price + atr * 2, price - atr

    # 🔻 BREAKOUT SAT
    if price < support and prev_price >= support and price < ema and rsi < 45:
        return "SAT", price, price - atr * 2, price + atr

    return None, None, None, None

# ================================
# TRADE VAR MI?
# ================================
def has_open_trade(symbol):
    for t in open_trades:
        if t["symbol"] == symbol:
            return True
    return False

# ================================
# TRADE KONTROL
# ================================
async def check_trades():
    global open_trades, balance

    for trade in open_trades[:]:
        df = get_data(trade['symbol'])

        if df is None:
            continue

        price = df['Close'].iloc[-1]

        # AL işlemi
        if trade['type'] == "AL":

            if price >= trade['target']:
                profit = trade['size'] * (trade['target'] - trade['entry'])
                balance += profit

                await bot.send_message(
                    CHAT_ID,
                    f"✅ {trade['symbol']} TP\n+{int(profit)} TL\nBakiye: {int(balance)}"
                )

                open_trades.remove(trade)

            elif price <= trade['stop']:
                loss = trade['size'] * (trade['entry'] - trade['stop'])
                balance -= loss

                await bot.send_message(
                    CHAT_ID,
                    f"❌ {trade['symbol']} SL\n-{int(loss)} TL\nBakiye: {int(balance)}"
                )

                open_trades.remove(trade)

        # SAT işlemi
        elif trade['type'] == "SAT":

            if price <= trade['target']:
                profit = trade['size'] * (trade['entry'] - trade['target'])
                balance += profit

                await bot.send_message(
                    CHAT_ID,
                    f"✅ {trade['symbol']} TP\n+{int(profit)} TL\nBakiye: {int(balance)}"
                )

                open_trades.remove(trade)

            elif price >= trade['stop']:
                loss = trade['size'] * (trade['stop'] - trade['entry'])
                balance -= loss

                await bot.send_message(
                    CHAT_ID,
                    f"❌ {trade['symbol']} SL\n-{int(loss)} TL\nBakiye: {int(balance)}"
                )

                open_trades.remove(trade)

# ================================
# ANA LOOP
# ================================
async def run():
    global open_trades

    print("🚀 Paper trading başladı")

    while True:
        for symbol in symbols:
            try:
                df = get_data(symbol)

                if df is None:
                    continue

                if has_open_trade(symbol):
                    continue

                signal, entry, target, stop = generate_signal(df)

                if signal:

                    trade = {
                        "symbol": symbol,
                        "type": signal,
                        "entry": entry,
                        "target": target,
                        "stop": stop,
                        "size": 10
                    }

                    open_trades.append(trade)

                    await bot.send_message(
                        CHAT_ID,
                        f"📊 {symbol}\n🚀 {signal}\nGiriş: {entry:.2f}\nTP: {target:.2f}\nSL: {stop:.2f}"
                    )

            except Exception as e:
                print("Hata:", symbol, e)

        await check_trades()
        await asyncio.sleep(300)

# ================================
# START
# ================================
if __name__ == "__main__":
    asyncio.run(run())