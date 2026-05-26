import yfinance as yf
import pandas as pd
import asyncio
import time
import json
from telegram import Bot

TOKEN = "8434925197:AAEzOTp4Q0zjRSlcHjQg8Mj9tvagXZHN1uI"
CHAT_ID = 1790584407

bot = Bot(token=TOKEN)

symbols = [
    "EREGL","THYAO","SASA","ASELS","KRDMD","ISCTR","GARAN","AKBNK",
    "YKBNK","SISE","PETKM","TUPRS","HEKTS","BIMAS","FROTO"
]

balance = 100000
RISK_PERCENT = 0.02
MAX_TRADES = 3

open_trades = []

AI_FILE = "ai_memory.json"

def load_ai():
    try:
        with open(AI_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_ai(data):
    with open(AI_FILE, "w") as f:
        json.dump(data, f)

ai_memory = load_ai()

# ================================
# PERFORMANCE
# ================================
total_trades = 0
win_trades = 0
lose_trades = 0
total_profit = 0
last_report_time = 0

# ================================
# INDICATORS
# ================================
def calculate_rsi(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(df):
    return df['Close'].ewm(span=200).mean()

def calculate_atr(df):
    tr = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - df['Close'].shift()).abs(),
        (df['Low'] - df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(14).mean().iloc[-1]

# ================================
# DATA
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
# ANALYZE
# ================================
def analyze(df, symbol):

    df['EMA'] = calculate_ema(df)
    df['RSI'] = calculate_rsi(df)

    try:
        price = df['Close'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        ema = df['EMA'].iloc[-1]
    except:
        return None

    resistance = df['High'].rolling(20).max().iloc[-1]
    atr = calculate_atr(df)

    if atr < price * 0.004:
        return None

    score = 0

    if price > ema:
        score += 25
    else:
        return None

    if rsi > 55:
        score += 25

    if price > resistance:
        score += 40
    else:
        if (resistance - price) / price < 0.03:
            score += 15

    target = resistance
    stop = price - atr
    rr = (target - price) / (price - stop)

    if rr > 2:
        score += 30
    elif rr > 1.3:
        score += 15
    else:
        return None

    confidence = score + (rr * 15)

    history = ai_memory.get(symbol, {"win":1,"loss":1})
    boost = (history["win"] / (history["win"] + history["loss"])) * 20
    confidence += boost

    return {
        "symbol": symbol,
        "price": price,
        "target": target,
        "stop": stop,
        "rr": rr,
        "score": score,
        "confidence": confidence
    }

# ================================
# POSITION
# ================================
def calculate_position(entry, stop):
    risk_amount = (balance * RISK_PERCENT) / MAX_TRADES
    risk_per_share = abs(entry - stop)

    if risk_per_share == 0:
        return 0

    return int(risk_amount / risk_per_share)

# ================================
# OPEN TRADE
# ================================
async def open_trade(trade):

    global total_trades

    qty = calculate_position(trade["price"], trade["stop"])

    if qty <= 0:
        return

    trade["size"] = qty
    open_trades.append(trade)
    total_trades += 1

    await bot.send_message(
        CHAT_ID,
        f"""🚀 TRADE

{trade['symbol']}
Giriş: {trade['price']:.2f}
TP: {trade['target']:.2f}
SL: {trade['stop']:.2f}
Lot: {qty}

Güven: {int(trade['confidence'])}
RR: {trade['rr']:.2f}"""
    )

# ================================
# CANLI TAKİP
# ================================
async def live_monitor():

    if not open_trades:
        return

    msg = "📡 CANLI DURUM\n\n"

    for trade in open_trades:

        df = get_data(trade["symbol"])
        if df is None:
            continue

        price = df['Close'].iloc[-1]
        entry = trade["price"]

        pnl = (price - entry) * trade["size"]
        pnl_pct = ((price - entry) / entry) * 100

        tp_distance = ((trade["target"] - price) / price) * 100
        sl_distance = ((price - trade["stop"]) / price) * 100

        msg += f"""{trade['symbol']}
Fiyat: {price:.2f}
PnL: {int(pnl)} TL ({pnl_pct:.2f}%)
TP mesafe: {tp_distance:.2f}%
SL mesafe: {sl_distance:.2f}%

"""

    await bot.send_message(CHAT_ID, msg)

# ================================
# CHECK TRADES
# ================================
async def check_trades():

    global balance, win_trades, lose_trades, total_profit

    for trade in open_trades[:]:

        df = get_data(trade["symbol"])
        if df is None:
            continue

        price = df['Close'].iloc[-1]
        entry = trade["price"]

        if price >= trade["target"]:
            profit = (trade["target"] - entry) * trade["size"]
            balance += profit
            total_profit += profit
            win_trades += 1

            update_ai(trade["symbol"], True)

            await bot.send_message(CHAT_ID, f"✅ TP {trade['symbol']} +{int(profit)} TL")
            open_trades.remove(trade)

        elif price <= trade["stop"]:
            loss = (entry - trade["stop"]) * trade["size"]
            balance -= loss
            total_profit -= loss
            lose_trades += 1

            update_ai(trade["symbol"], False)

            await bot.send_message(CHAT_ID, f"❌ SL {trade['symbol']} -{int(loss)} TL")
            open_trades.remove(trade)

# ================================
# AI UPDATE
# ================================
def update_ai(symbol, win):
    data = ai_memory.get(symbol, {"win": 0, "loss": 0})

    if win:
        data["win"] += 1
    else:
        data["loss"] += 1

    ai_memory[symbol] = data
    save_ai(ai_memory)

# ================================
# MAIN LOOP
# ================================
async def run():

    print("📡 LIVE BOT AKTİF")
    await bot.send_message(CHAT_ID, "📡 CANLI BOT BAŞLADI")

    while True:

        results = []

        for symbol in symbols:

            df = get_data(symbol)
            if df is None:
                continue

            result = analyze(df, symbol)

            if result:
                results.append(result)

        top = sorted(results, key=lambda x: x["confidence"], reverse=True)[:MAX_TRADES]

        for trade in top:
            if len(open_trades) < MAX_TRADES:
                await open_trade(trade)

        await check_trades()
        await live_monitor()

        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(run())