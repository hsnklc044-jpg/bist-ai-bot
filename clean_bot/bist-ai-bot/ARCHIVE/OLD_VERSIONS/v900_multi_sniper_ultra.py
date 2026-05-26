import yfinance as yf
import requests
import time
import pandas as pd
from datetime import datetime

# ================== AYARLAR ==================
TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = [
    "EREGL.IS","THYAO.IS","SISE.IS","KRDMD.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","AKBNK.IS","YKBNK.IS","GARAN.IS"
]

INTERVAL = "1m"
PERIOD = "1d"

# 🔥 DENGELİ (PRO) PARAMETRELER
MIN_BARS = 60
RSI_LEN = 14
ATR_LEN = 14

WICK_MIN = 0.35
VOL_SPIKE_MULT = 1.15
BASE_THRESHOLD = 4

SCAN_SLEEP = 15
COOLDOWN = 120

SL_ATR = 1.2
TP_ATR = 2.0

last_signal_time = 0
position = None
last_alert = None

# ================== TELEGRAM ==================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

# ================== İNDİKATÖRLER ==================
def rsi(df, n=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    ag = gain.rolling(n).mean()
    al = loss.rolling(n).mean()
    rs = ag / al
    return 100 - (100 / (1 + rs))

def atr(df, n=14):
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift()).abs()
    lc = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# ================== DATA ==================
def get_data(symbol):
    try:
        df = yf.download(symbol, interval=INTERVAL, period=PERIOD, progress=False)
        if df is None or df.empty or len(df) < MIN_BARS:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df
    except:
        return None

# ================== ANALİZ ==================
def analyze(symbol, df):
    df = df.copy()

    df['rsi'] = rsi(df, RSI_LEN)
    df['atr'] = atr(df, ATR_LEN)
    df['ema20'] = df['Close'].ewm(span=20).mean()
    df['ema50'] = df['Close'].ewm(span=50).mean()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    def s(x):
        if isinstance(x, pd.Series):
            x = x.item()
        return float(x) if not pd.isna(x) else None

    r = s(last['rsi'])
    atr_v = s(last['atr'])
    vol = s(last['Volume'])
    o, c, h, l = s(last['Open']), s(last['Close']), s(last['High']), s(last['Low'])
    ema20, ema50 = s(last['ema20']), s(last['ema50'])

    if None in [r, atr_v, vol, o, c, h, l]:
        return None

    # 🔥 Wick (range normalize)
    rng = (h - l) + 1e-9
    up_w = h - max(o, c)
    lo_w = min(o, c) - l

    buy_w = lo_w / rng
    sell_w = up_w / rng

    # 🔥 Volume spike (relatif)
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    vol_ok = vol > (avg_vol * VOL_SPIKE_MULT if pd.notna(avg_vol) else 0)

    # 🔥 Trend
    trend_up = ema20 > ema50
    trend_dn = ema20 < ema50

    # 🔥 Fake breakout
    prev_high = df['High'].rolling(20).max().shift(1).iloc[-1]
    prev_low  = df['Low'].rolling(20).min().shift(1).iloc[-1]

    fake_up = (h > prev_high) and (c < prev_high)
    fake_dn = (l < prev_low) and (c > prev_low)

    # ================== SKOR ==================
    score_buy = 0
    score_sell = 0

    # BUY
    if buy_w > WICK_MIN: score_buy += 2
    if r < 50: score_buy += 1
    if vol_ok: score_buy += 2
    if fake_dn: score_buy += 1
    if trend_up: score_buy += 1

    # SELL
    if sell_w > WICK_MIN: score_sell += 2
    if r > 50: score_sell += 1
    if vol_ok: score_sell += 2
    if fake_up: score_sell += 1
    if trend_dn: score_sell += 1

    # 🔥 Dinamik threshold
    threshold = BASE_THRESHOLD

    side = None
    score = 0

    if score_buy >= threshold and score_buy > score_sell:
        side = "BUY"
        score = score_buy
    elif score_sell >= threshold and score_sell > score_buy:
        side = "SELL"
        score = score_sell
    else:
        return None

    # 🔥 SL / TP
    if side == "BUY":
        sl = c - SL_ATR * atr_v
        tp = c + TP_ATR * atr_v
    else:
        sl = c + SL_ATR * atr_v
        tp = c - TP_ATR * atr_v

    return {
        "symbol": symbol,
        "side": side,
        "score": score,
        "rsi": r,
        "price": c,
        "volume": vol,
        "avg_vol": float(avg_vol) if pd.notna(avg_vol) else 0,
        "buy_w": buy_w,
        "sell_w": sell_w,
        "sl": sl,
        "tp": tp
    }

# ================== SCAN ==================
def scan_market():
    results = []

    for sym in SYMBOLS:
        df = get_data(sym)
        if df is None:
            continue

        res = analyze(sym, df)
        if res:
            results.append(res)

    if not results:
        return None

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[0]

# ================== MAIN ==================
print("🚀 V900 MULTI SNIPER PRO FINAL STARTED")
send_telegram("🧠 V900 PRO BOT STARTED")

while True:
    try:
        now = time.time()

        if (now - last_signal_time) < COOLDOWN:
            print("⏳ COOLDOWN")
            time.sleep(SCAN_SLEEP)
            continue

        best = scan_market()

        if best is None:
            print("❌ NO SIGNAL")
            time.sleep(SCAN_SLEEP)
            continue

        sym = best["symbol"]
        side = best["side"]

        if last_alert == (sym, side):
            print("⏭ DUPLICATE SKIP")
            time.sleep(SCAN_SLEEP)
            continue

        if side == "BUY" and position is None:
            position = "LONG"
        elif side == "SELL" and position == "LONG":
            position = None
        else:
            time.sleep(SCAN_SLEEP)
            continue

        last_signal_time = now
        last_alert = (sym, side)

        msg = (
            f"{'🟢 BUY' if side=='BUY' else '🔴 SELL'} {sym}\n"
            f"Score: {best['score']}\n"
            f"RSI: {best['rsi']:.2f}\n"
            f"VOL: {int(best['volume'])} (avg {int(best['avg_vol'])})\n"
            f"Price: {best['price']:.2f}\n"
            f"Wick: {best['buy_w']:.2f}/{best['sell_w']:.2f}\n"
            f"SL: {best['sl']:.2f} | TP: {best['tp']:.2f}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )

        print(msg)
        send_telegram(msg)

        time.sleep(SCAN_SLEEP)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(SCAN_SLEEP)