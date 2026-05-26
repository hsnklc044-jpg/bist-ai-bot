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
SCAN_SLEEP = 3   # hızlı tarama

ACCOUNT_SIZE = 100000
RISK_PER_TRADE = 0.02
MAX_TOTAL_RISK = 0.05
MAX_SCALE_RISK = 0.02

MAX_POSITIONS = 3
MAX_SCALE = 2

SL_ATR = 1.0
TP_ATR = 2.0
TRAIL_ATR = 0.8

DRAWDOWN_LIMIT = -0.05

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
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
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

    # fake breakout
    prev_high = df['High'].rolling(20).max().shift(1).iloc[-1]
    prev_low = df['Low'].rolling(20).min().shift(1).iloc[-1]
    fake_up = (h > prev_high) and (c < prev_high)
    fake_down = (l < prev_low) and (c > prev_low)

    score_buy = (buy_w>0.3)*2 + (r<50)*1 + vol_ok*2 + fake_down*1
    score_sell = (sell_w>0.3)*2 + (r>50)*1 + vol_ok*2 + fake_up*1

    if score_buy>score_sell and score_buy>=3:
        return {"sym":sym,"side":"LONG","price":c,"atr":atr_v,"score":score_buy}
    elif score_sell>=3:
        return {"sym":sym,"side":"SHORT","price":c,"atr":atr_v,"score":score_sell}
    return None

# ================== MAIN ==================
print("🚀 INSTITUTIONAL LIVE SYSTEM STARTED")
send("🧠 SYSTEM STARTED")

while True:
    try:
        print("\n⏱", datetime.now().strftime("%H:%M:%S"))

        # drawdown kontrol
        drawdown = (equity - peak_equity) / peak_equity
        if drawdown <= DRAWDOWN_LIMIT:
            print("🛑 DRAWDOWN LIMIT! STOP")
            time.sleep(SCAN_SLEEP)
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
                entry = pos["entry"]
                atr = pos["atr"]
                side = pos["side"]

                pos["trail"] = pos.get("trail", entry)

                exit_signal = False

                if side == "LONG":
                    pos["trail"] = max(pos["trail"], price)
                    if price <= entry - SL_ATR*atr: reason="SL"; exit_signal=True
                    elif price >= entry + TP_ATR*atr: reason="TP"; exit_signal=True
                    elif price <= pos["trail"] - TRAIL_ATR*atr: reason="TRAIL"; exit_signal=True
                    elif sig["side"]=="SHORT": reason="REVERSAL"; exit_signal=True

                    if exit_signal:
                        pnl = (price-entry)*pos["size"]

                else:
                    pos["trail"] = min(pos["trail"], price)
                    if price >= entry + SL_ATR*atr: reason="SL"; exit_signal=True
                    elif price <= entry - TP_ATR*atr: reason="TP"; exit_signal=True
                    elif price >= pos["trail"] + TRAIL_ATR*atr: reason="TRAIL"; exit_signal=True
                    elif sig["side"]=="LONG": reason="REVERSAL"; exit_signal=True

                    if exit_signal:
                        pnl = (entry-price)*pos["size"]

                if exit_signal:
                    equity += pnl
                    total_pnl += pnl
                    trade_count += 1
                    if pnl>0: win_count+=1

                    print(f"❌ EXIT {sym} {reason} PnL:{pnl:.2f}")
                    log_trade([datetime.now(),sym,side,entry,price,pnl])
                    del positions[sym]
                    continue

                # SCALE IN (kontrollü)
                now = time.time()
                if sig["side"]==side and pos.get("scale",0)<MAX_SCALE:
                    if can_scale() and sig["score"]>=5:
                        if now - pos.get("last_scale_time",0) > 60:
                            pos["size"] *= 1.2
                            pos["scale"] = pos.get("scale",0)+1
                            pos["last_scale_time"] = now
                            print(f"🔥 SCALE {sym}")

                # SCALE OUT (kâr kilitle)
                if side=="LONG" and price > entry*1.02:
                    pos["size"] *= 0.7
                    print("💰 SCALE OUT LONG", sym)

                if side=="SHORT" and price < entry*0.98:
                    pos["size"] *= 0.7
                    print("💰 SCALE OUT SHORT", sym)

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

            winrate = (win_count/trade_count*100) if trade_count>0 else 0

            msg = f"{sig['side']} {sym}\nPrice:{price:.2f}\nSize:{size}\nPnL:{total_pnl:.2f}\nWinrate:{winrate:.1f}%"
            print("🚀", msg)
            send(msg)

        peak_equity = max(peak_equity, equity)
        time.sleep(SCAN_SLEEP)

    except Exception as e:
        print("❌ hata:", e)
        time.sleep(SCAN_SLEEP)