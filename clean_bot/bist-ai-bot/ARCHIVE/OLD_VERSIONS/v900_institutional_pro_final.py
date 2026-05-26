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

ACCOUNT_SIZE = 100000
RISK_PER_TRADE = 0.02
MAX_TOTAL_RISK = 0.05
MAX_SCALE_RISK = 0.02

MAX_POSITIONS = 3
MAX_SCALE = 2

SL_ATR = 1.0
TP_ATR = 2.0
TRAIL_ATR = 0.8

DRAWDOWN_LIMIT = -0.05   # -%5 stop sistemi

LOG_FILE = "trades.csv"

# ================== STATE ==================
positions = {}
total_pnl = 0
equity = ACCOUNT_SIZE
peak_equity = ACCOUNT_SIZE

trade_count = 0
win_count = 0

# ================== TELEGRAM ==================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ================== LOG ==================
def log_trade(row):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE,"a",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["time","symbol","side","entry","exit","pnl"])
        w.writerow(row)

# ================== RISK ==================
def current_total_risk():
    return len(positions) * RISK_PER_TRADE

def can_scale():
    return current_total_risk() < (MAX_TOTAL_RISK + MAX_SCALE_RISK)

def calc_size(price, atr):
    risk_amount = ACCOUNT_SIZE * RISK_PER_TRADE
    sl_distance = atr * SL_ATR
    if sl_distance == 0:
        return 0
    return round(risk_amount / (sl_distance * price), 2)

# ================== INDICATORS ==================
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

# ================== ANALYZE ==================
def analyze(sym, df):
    df['rsi'] = rsi(df)
    df['atr'] = atr(df)
    last = df.iloc[-1]

    r = float(last['rsi'])
    o,c,h,l = float(last['Open']),float(last['Close']),float(last['High']),float(last['Low'])
    vol = float(last['Volume'])
    atr_v = float(last['atr'])

    rng = (h-l)+1e-9
    buy_w = (min(o,c)-l)/rng
    sell_w = (h-max(o,c))/rng

    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    vol_ok = vol > avg_vol*1.1 if pd.notna(avg_vol) else False

    score_buy = (buy_w>0.3)*2 + (r<50)*1 + vol_ok*2
    score_sell = (sell_w>0.3)*2 + (r>50)*1 + vol_ok*2

    if score_buy>score_sell and score_buy>=3:
        return {"sym":sym,"side":"LONG","price":c,"atr":atr_v,"score":score_buy}
    elif score_sell>=3:
        return {"sym":sym,"side":"SHORT","price":c,"atr":atr_v,"score":score_sell}
    return None

# ================== MAIN ==================
print("🚀 INSTITUTIONAL PRO SYSTEM STARTED")
send("🧠 INSTITUTIONAL PRO SYSTEM STARTED")

while True:
    try:
        print("\n⏱", datetime.now().strftime("%H:%M:%S"))

        # ================== DRAWDOWN CONTROL ==================
        drawdown = (equity - peak_equity) / peak_equity
        if drawdown <= DRAWDOWN_LIMIT:
            print("🛑 DRAWDOWN LIMIT! Sistem durdu")
            continue

        for sym in SYMBOLS:
            df = get(sym)
            if df is None:
                continue

            sig = analyze(sym, df)
            if sig is None:
                continue

            price = sig["price"]
            atr_v = sig["atr"]

            # ================== EXIT ==================
            if sym in positions:
                pos = positions[sym]

                # SCALE OUT (kâr al)
                if pos["side"]=="LONG" and price > pos["entry"]*1.02:
                    pos["size"] *= 0.7
                    print("💰 SCALE OUT LONG", sym)

                if pos["side"]=="SHORT" and price < pos["entry"]*0.98:
                    pos["size"] *= 0.7
                    print("💰 SCALE OUT SHORT", sym)

                # SL / TP / TRAIL
                if pos["side"]=="LONG":
                    if price <= pos["entry"] - SL_ATR*pos["atr"] or price < pos.get("trail",pos["entry"]) - TRAIL_ATR*pos["atr"]:
                        pnl = (price-pos["entry"])*pos["size"]
                    elif price >= pos["entry"] + TP_ATR*pos["atr"]:
                        pnl = (price-pos["entry"])*pos["size"]
                    else:
                        pos["trail"] = max(pos.get("trail", pos["entry"]), price)
                        continue

                else:
                    if price >= pos["entry"] + SL_ATR*pos["atr"] or price > pos.get("trail",pos["entry"]) + TRAIL_ATR*pos["atr"]:
                        pnl = (pos["entry"]-price)*pos["size"]
                    elif price <= pos["entry"] - TP_ATR*pos["atr"]:
                        pnl = (pos["entry"]-price)*pos["size"]
                    else:
                        pos["trail"] = min(pos.get("trail", pos["entry"]), price)
                        continue

                # CLOSE
                equity += pnl
                total_pnl += pnl
                trade_count += 1
                if pnl>0: win_count+=1

                log_trade([datetime.now(),sym,pos["side"],pos["entry"],price,pnl])
                del positions[sym]
                print("❌ EXIT", sym, pnl)
                continue

            # ================== ENTRY ==================
            if len(positions) >= MAX_POSITIONS:
                continue

            if current_total_risk() >= MAX_TOTAL_RISK:
                continue

            size = calc_size(price, atr_v)
            if size <= 0:
                continue

            positions[sym] = {
                "side": sig["side"],
                "entry": price,
                "size": size,
                "atr": atr_v,
                "trail": price,
                "scale": 0,
                "last_scale_time": 0
            }

            msg = f"{sig['side']} {sym}\nPrice:{price:.2f}\nSize:{size}\nPnL:{total_pnl:.2f}"
            print("🚀", msg)
            send(msg)

        peak_equity = max(peak_equity, equity)
        time.sleep(SCAN_SLEEP)

    except Exception as e:
        print("❌ hata", e)
        time.sleep(SCAN_SLEEP)