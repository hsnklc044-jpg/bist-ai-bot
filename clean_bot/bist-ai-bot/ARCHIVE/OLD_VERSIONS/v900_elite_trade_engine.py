import yfinance as yf
import requests
import time
import pandas as pd
from datetime import datetime
import csv, os

# ================== AYARLAR ==================
TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS","THYAO.IS","ASELS.IS"]

INTERVAL = "1m"
PERIOD = "1d"

SCAN_SLEEP = 10
COOLDOWN = 60

RISK_PER_TRADE = 0.02   # %2 risk
ACCOUNT_SIZE = 100000   # demo

WICK_MIN = 0.3
VOL_SPIKE = 1.1

SL_ATR = 1.0
TP_ATR = 2.0
TRAIL_ATR = 0.8

MAX_POSITION_SIZE = 3   # scale max

LOG_FILE = "trades.csv"

# ================== STATE ==================
positions = {}   # symbol: {side, entry, size, atr, trail}
last_signal_time = 0
total_pnl = 0

# ================== TELEGRAM ==================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ================== LOG ==================
def log(row):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE,"a",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["time","symbol","side","entry","exit","pnl"])
        w.writerow(row)

# ================== İNDİKATÖRLER ==================
def rsi(df):
    d = df['Close'].diff()
    gain = d.clip(lower=0).rolling(14).mean()
    loss = (-d.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100/(1+rs))

def atr(df):
    tr = pd.concat([
        df['High']-df['Low'],
        (df['High']-df['Close'].shift()).abs(),
        (df['Low']-df['Close'].shift()).abs()
    ],axis=1).max(axis=1)
    return tr.rolling(14).mean()

# ================== DATA ==================
def get(symbol):
    try:
        df = yf.download(symbol, interval=INTERVAL, period=PERIOD, progress=False)
        if df is None or df.empty or len(df)<50:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

# ================== ANALİZ ==================
def analyze(sym, df):
    df['rsi'] = rsi(df)
    df['atr'] = atr(df)
    df['ema20'] = df['Close'].ewm(span=20).mean()
    df['ema50'] = df['Close'].ewm(span=50).mean()

    last = df.iloc[-1]

    r = float(last['rsi'])
    o,c,h,l = float(last['Open']),float(last['Close']),float(last['High']),float(last['Low'])
    vol = float(last['Volume'])
    atr_v = float(last['atr'])

    rng = (h-l)+1e-9
    buy_w = (min(o,c)-l)/rng
    sell_w = (h-max(o,c))/rng

    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    vol_ok = vol > avg_vol*VOL_SPIKE if pd.notna(avg_vol) else False

    score_buy = 0
    score_sell = 0

    if buy_w > WICK_MIN: score_buy+=2
    if r < 50: score_buy+=1
    if vol_ok: score_buy+=2

    if sell_w > WICK_MIN: score_sell+=2
    if r > 50: score_sell+=1
    if vol_ok: score_sell+=2

    if score_buy > score_sell and score_buy>=3:
        return {"sym":sym,"side":"LONG","price":c,"atr":atr_v,"score":score_buy}
    elif score_sell>=3:
        return {"sym":sym,"side":"SHORT","price":c,"atr":atr_v,"score":score_sell}
    return None

# ================== POSITION SIZE ==================
def calc_size(price, atr):
    risk_amount = ACCOUNT_SIZE * RISK_PER_TRADE
    sl_distance = atr * SL_ATR
    size = risk_amount / sl_distance if sl_distance>0 else 0
    return round(size,2)

# ================== MAIN ==================
print("🚀 ELITE ENGINE STARTED")
send("🧠 ELITE ENGINE STARTED")

while True:
    try:
        print("\n⏱ tarama", datetime.now().strftime("%H:%M:%S"))

        for sym in SYMBOLS:
            df = get(sym)
            if df is None:
                continue

            sig = analyze(sym, df)
            if sig is None:
                continue

            price = sig["price"]
            atr_v = sig["atr"]

            # ================== POSITION VARSA ==================
            if sym in positions:
                pos = positions[sym]

                # TRAILING
                if pos["side"]=="LONG":
                    pos["trail"] = max(pos["trail"], price)
                    if price < pos["trail"] - TRAIL_ATR*pos["atr"]:
                        pnl = (price - pos["entry"])*pos["size"]
                        total_pnl += pnl
                        print("📉 LONG EXIT", pnl)
                        log([datetime.now(),sym,"LONG",pos["entry"],price,pnl])
                        del positions[sym]

                elif pos["side"]=="SHORT":
                    pos["trail"] = min(pos["trail"], price)
                    if price > pos["trail"] + TRAIL_ATR*pos["atr"]:
                        pnl = (pos["entry"] - price)*pos["size"]
                        total_pnl += pnl
                        print("📉 SHORT EXIT", pnl)
                        log([datetime.now(),sym,"SHORT",pos["entry"],price,pnl])
                        del positions[sym]

                # SCALE
                if sig["side"] == pos["side"] and pos["size"] < MAX_POSITION_SIZE:
                    print("🔥 SCALE IN", sym)
                    pos["size"] += 1

                continue

            # ================== YENİ ENTRY ==================
            size = calc_size(price, atr_v)

            positions[sym] = {
                "side": sig["side"],
                "entry": price,
                "size": size,
                "atr": atr_v,
                "trail": price
            }

            msg = f"{'🟢 LONG' if sig['side']=='LONG' else '🔴 SHORT'} {sym}\nPrice: {price}\nSize: {size}\nScore:{sig['score']}\nTotalPnL:{total_pnl:.2f}"

            print("🚀", msg)
            send(msg)

        time.sleep(SCAN_SLEEP)

    except Exception as e:
        print("❌ hata", e)
        time.sleep(SCAN_SLEEP)