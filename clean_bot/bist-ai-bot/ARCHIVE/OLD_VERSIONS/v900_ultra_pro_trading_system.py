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

MIN_BARS = 60
RSI_LEN = 14
ATR_LEN = 14

WICK_MIN = 0.30
VOL_SPIKE_MULT = 1.10
BASE_THRESHOLD = 3

SCAN_SLEEP = 15
COOLDOWN = 90

SL_ATR = 1.2
TP_ATR = 2.0

# ================== STATE ==================
position = None          # None / LONG / SHORT
entry_price = 0
last_signal_time = 0
last_alert = None
total_pnl = 0

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
    rs = gain.rolling(n).mean() / loss.rolling(n).mean()
    return 100 - (100 / (1 + rs))

def atr(df, n=14):
    tr = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - df['Close'].shift()).abs(),
        (df['Low'] - df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# ================== DATA ==================
def get_data(symbol):
    try:
        df = yf.download(symbol, interval=INTERVAL, period=PERIOD, progress=False, threads=False)
        if df is None or df.empty or len(df) < MIN_BARS:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df
    except:
        return None

# ================== ANALİZ ==================
def analyze(symbol, df):
    try:
        df = df.copy()

        df['rsi'] = rsi(df)
        df['atr'] = atr(df)
        df['ema20'] = df['Close'].ewm(span=20).mean()
        df['ema50'] = df['Close'].ewm(span=50).mean()

        last = df.iloc[-1]

        r = float(last['rsi'])
        o, c, h, l = float(last['Open']), float(last['Close']), float(last['High']), float(last['Low'])
        vol = float(last['Volume'])
        atr_v = float(last['atr'])
        ema20 = float(last['ema20'])
        ema50 = float(last['ema50'])

        rng = (h - l) + 1e-9
        buy_w = (min(o, c) - l) / rng
        sell_w = (h - max(o, c)) / rng

        avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
        vol_ok = vol > avg_vol * VOL_SPIKE_MULT if pd.notna(avg_vol) else False

        trend_up = ema20 > ema50
        trend_dn = ema20 < ema50

        prev_high = df['High'].rolling(20).max().shift(1).iloc[-1]
        prev_low = df['Low'].rolling(20).min().shift(1).iloc[-1]

        fake_up = (h > prev_high) and (c < prev_high)
        fake_dn = (l < prev_low) and (c > prev_low)

        score_buy = 0
        score_sell = 0

        if buy_w > WICK_MIN: score_buy += 2
        if r < 50: score_buy += 1
        if vol_ok: score_buy += 2
        if fake_dn: score_buy += 1
        if trend_up: score_buy += 1

        if sell_w > WICK_MIN: score_sell += 2
        if r > 50: score_sell += 1
        if vol_ok: score_sell += 2
        if fake_up: score_sell += 1
        if trend_dn: score_sell += 1

        if score_buy >= BASE_THRESHOLD and score_buy > score_sell:
            return {"symbol":symbol,"side":"BUY","price":c,"score":score_buy}
        elif score_sell >= BASE_THRESHOLD:
            return {"symbol":symbol,"side":"SELL","price":c,"score":score_sell}
        else:
            return None

    except:
        return None

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

    if results:
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[0]

    return None

# ================== MAIN ==================
print("🚀 ULTRA PRO TRADING SYSTEM STARTED")
send_telegram("🧠 ULTRA PRO TRADING SYSTEM STARTED")

while True:
    try:
        print(f"\n⏱ {datetime.now().strftime('%H:%M:%S')} tarama...")

        now = time.time()

        if now - last_signal_time < COOLDOWN:
            print("⏳ cooldown")
            time.sleep(SCAN_SLEEP)
            continue

        best = scan_market()

        if best is None:
            print("❌ sinyal yok")
            time.sleep(SCAN_SLEEP)
            continue

        sym = best["symbol"]
        side = best["side"]
        price = best["price"]

        print(f"📊 {sym} {side} bulundu @ {price}")

        if last_alert == (sym, side):
            print("⏭ duplicate")
            time.sleep(SCAN_SLEEP)
            continue

        pnl = 0

        # ================== POZİSYON ==================
        if side == "BUY":
            if position is None:
                position = "LONG"
                entry_price = price
                print("🟢 LONG AÇILDI")

            elif position == "SHORT":
                pnl = entry_price - price
                total_pnl += pnl
                print(f"💰 SHORT KAPANDI PnL: {pnl:.2f}")
                position = None

        elif side == "SELL":
            if position is None:
                position = "SHORT"
                entry_price = price
                print("🔴 SHORT AÇILDI")

            elif position == "LONG":
                pnl = price - entry_price
                total_pnl += pnl
                print(f"💰 LONG KAPANDI PnL: {pnl:.2f}")
                position = None

        last_signal_time = now
        last_alert = (sym, side)

        msg = (
            f"{'🟢 BUY' if side=='BUY' else '🔴 SELL'} {sym}\n"
            f"Price: {price:.2f}\n"
            f"Score: {best['score']}\n"
            f"Total PnL: {total_pnl:.2f}"
        )

        print("🚀 gönderildi:", msg)
        send_telegram(msg)

        time.sleep(SCAN_SLEEP)

    except Exception as e:
        print("❌ hata:", e)
        time.sleep(SCAN_SLEEP)