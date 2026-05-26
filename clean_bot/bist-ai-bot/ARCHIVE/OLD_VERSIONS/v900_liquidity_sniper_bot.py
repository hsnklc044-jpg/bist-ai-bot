import yfinance as yf
import requests
import time
import pandas as pd

# ================== AYARLAR ==================
TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOL = "EREGL.IS"
INTERVAL = "1m"

MIN_VOLUME = 10_000_000
RSI_LOW = 30
RSI_HIGH = 70
WICK_RATIO = 2.0

COOLDOWN = 60

last_signal_time = 0
position = None

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
def get_data():
    df = yf.download(
        SYMBOL,
        interval=INTERVAL,
        period="1d",
        progress=False
    )

    if df is None or df.empty:
        return None

    # 🔥 MultiIndex düzelt
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df

# ================== STRATEJİ ==================
def check_trade(df):
    df['rsi'] = calculate_rsi(df)

    last = df.iloc[-1]

    # 🔥 %100 scalar garanti
    rsi = last['rsi']
    volume = last['Volume']
    open_ = last['Open']
    close = last['Close']
    high = last['High']
    low = last['Low']

    # 👉 Series ise zorla scalar yap
    if isinstance(rsi, pd.Series): rsi = rsi.item()
    if isinstance(volume, pd.Series): volume = volume.item()
    if isinstance(open_, pd.Series): open_ = open_.item()
    if isinstance(close, pd.Series): close = close.item()
    if isinstance(high, pd.Series): high = high.item()
    if isinstance(low, pd.Series): low = low.item()

    # 👉 float güvence
    rsi = float(rsi) if not pd.isna(rsi) else None
    volume = float(volume)
    open_ = float(open_)
    close = float(close)
    high = float(high)
    low = float(low)

    reasons = []

    if rsi is None:
        return None, ["RSI_NOT_READY"], None, None

    if volume < MIN_VOLUME:
        reasons.append("LOW_VOLUME")

    if rsi > RSI_HIGH:
        reasons.append("RSI_HIGH")

    if rsi < RSI_LOW:
        reasons.append("RSI_LOW")

    body = abs(close - open_)
    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low

    buy_signal = lower_wick > body * WICK_RATIO
    sell_signal = upper_wick > body * WICK_RATIO

    if not buy_signal and not sell_signal:
        reasons.append("NO_WICK_SIGNAL")

    if reasons:
        return None, reasons, rsi, volume

    if buy_signal:
        return "BUY", [], rsi, volume

    if sell_signal:
        return "SELL", [], rsi, volume

# ================== MAIN ==================
print("🚀 V900 REAL DATA (ULTRA STABLE) STARTED")
send_telegram("🧠 V900 ULTRA STABLE BOT STARTED")

while True:
    try:
        df = get_data()

        if df is None:
            print("❌ VERİ YOK")
            time.sleep(10)
            continue

        signal, reasons, rsi, volume = check_trade(df)

        now = time.time()

        if (now - last_signal_time) < COOLDOWN:
            print("⏳ COOLDOWN")
            time.sleep(10)
            continue

        if signal == "BUY" and position is None:
            position = "BUY"
            last_signal_time = now

            msg = f"🟢 BUY {SYMBOL}\nRSI: {rsi:.2f}\nVOL: {int(volume)}"
            print(msg)
            send_telegram(msg)

        elif signal == "SELL" and position == "BUY":
            position = None
            last_signal_time = now

            msg = f"🔴 SELL {SYMBOL}\nRSI: {rsi:.2f}\nVOL: {int(volume)}"
            print(msg)
            send_telegram(msg)

        else:
            print(f"❌ NO TRADE → {reasons} | RSI: {rsi} | VOL: {volume} | POS: {position}")

        time.sleep(10)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(10)