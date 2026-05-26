import yfinance as yf
import requests
import time
import pandas as pd
from datetime import datetime

# ================== AYARLAR ==================
TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

# BIST sembolleri (istediğin kadar ekle)
SYMBOLS = [
    "EREGL.IS", "THYAO.IS", "SISE.IS", "KRDMD.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "AKBNK.IS", "YKBNK.IS", "GARAN.IS"
]

INTERVAL = "1m"
PERIOD = "1d"

# Filtreler
RSI_LOW = 30
RSI_HIGH = 70
WICK_RATIO = 1.8          # daha gerçekçi
VOL_SPIKE_MULT = 1.3      # ortalamanın %30 üstü
MIN_BARS = 40

# Sistem
SCAN_SLEEP = 15           # saniye
COOLDOWN = 120            # sinyal sonrası bekleme

# Global state
last_signal_time = 0
position = None           # None / "LONG"
last_alert = None         # (symbol, side)

# ================== TELEGRAM ==================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

# ================== RSI ==================
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ================== DATA ==================
def get_data(symbol):
    try:
        df = yf.download(symbol, interval=INTERVAL, period=PERIOD, progress=False)
        if df is None or df.empty or len(df) < MIN_BARS:
            return None

        # MultiIndex düzelt
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df
    except:
        return None

# ================== ANALİZ ==================
def analyze(symbol, df):
    df = df.copy()
    df['rsi'] = calculate_rsi(df)

    last = df.iloc[-1]

    # scalar garanti
    def scalar(x):
        if isinstance(x, pd.Series):
            x = x.item()
        return float(x) if not pd.isna(x) else None

    rsi = scalar(last['rsi'])
    volume = scalar(last['Volume'])
    open_ = scalar(last['Open'])
    close = scalar(last['Close'])
    high = scalar(last['High'])
    low = scalar(last['Low'])

    if rsi is None:
        return None

    # ---- Wick (likidite) ----
    body = abs(close - open_) + 1e-9
    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low

    buy_wick = lower_wick / body
    sell_wick = upper_wick / body

    # ---- Volume spike (relatif) ----
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    vol_ok = volume > (avg_vol * VOL_SPIKE_MULT if pd.notna(avg_vol) else 0)

    # ---- Skor sistemi ----
    score = 0
    side = None

    # BUY koşulları
    if buy_wick > WICK_RATIO:
        score += 2
        side = "BUY"
    if rsi < 45:
        score += 1
    if vol_ok:
        score += 2

    # SELL koşulları
    if sell_wick > WICK_RATIO:
        if side is None:
            side = "SELL"
        score += 2
    if rsi > 55:
        score += 1
    if vol_ok:
        score += 2

    # Gürültüyü azalt
    if score < 4 or side is None:
        return None

    return {
        "symbol": symbol,
        "side": side,
        "score": score,
        "rsi": rsi,
        "volume": volume,
        "avg_vol": float(avg_vol) if pd.notna(avg_vol) else 0.0,
        "price": close,
        "buy_wick": buy_wick,
        "sell_wick": sell_wick
    }

# ================== SCANNER ==================
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

    # en yüksek skorluyu seç
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[0]

# ================== MAIN ==================
print("🚀 V900 MULTI SNIPER PRO STARTED")
send_telegram("🧠 V900 MULTI SNIPER PRO STARTED")

while True:
    try:
        now = time.time()

        # cooldown
        if (now - last_signal_time) < COOLDOWN:
            print("⏳ COOLDOWN")
            time.sleep(SCAN_SLEEP)
            continue

        best = scan_market()

        if best is None:
            print("❌ NO SIGNAL")
            time.sleep(SCAN_SLEEP)
            continue

        symbol = best["symbol"]
        side = best["side"]

        # duplicate engelle
        if last_alert == (symbol, side):
            print(f"⏭ SKIP DUPLICATE {symbol} {side}")
            time.sleep(SCAN_SLEEP)
            continue

        # pozisyon mantığı
        if side == "BUY" and position is None:
            position = "LONG"
        elif side == "SELL" and position == "LONG":
            position = None
        else:
            print(f"⏭ SKIP POS {symbol} {side} POS={position}")
            time.sleep(SCAN_SLEEP)
            continue

        last_signal_time = now
        last_alert = (symbol, side)

        msg = (
            f"{'🟢 BUY' if side=='BUY' else '🔴 SELL'} {symbol}\n"
            f"Score: {best['score']}\n"
            f"RSI: {best['rsi']:.2f}\n"
            f"VOL: {int(best['volume'])} (avg {int(best['avg_vol'])})\n"
            f"Price: {best['price']:.2f}\n"
            f"Wick(b/s): {best['buy_wick']:.2f}/{best['sell_wick']:.2f}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )

        print(msg)
        send_telegram(msg)

        time.sleep(SCAN_SLEEP)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(SCAN_SLEEP)