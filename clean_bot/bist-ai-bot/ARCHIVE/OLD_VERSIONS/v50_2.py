import time
import requests
import pandas as pd
import numpy as np

BOT_TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

LAST_SIGNAL = {}
SCORE_MEMORY = {}

COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "BNBUSDT"]

def get_data(symbol, interval="5m", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","o","h","l","c","v","ct","qv","n","tb","tq","ig"
    ])

    df["c"] = df["c"].astype(float)
    return df

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_score(df):
    close = df["c"]

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    rsi = calculate_rsi(close)

    trend = "UP" if ema20.iloc[-1] > ema50.iloc[-1] else "DOWN"

    score = 0

    if trend == "UP":
        score += 40

    if 40 < rsi.iloc[-1] < 65:
        score += 30

    if close.iloc[-1] > close.iloc[-5]:
        score += 30

    return score, rsi.iloc[-1], trend

def smooth_score(symbol, new_score, alpha=0.3):
    if symbol not in SCORE_MEMORY:
        SCORE_MEMORY[symbol] = new_score
    else:
        SCORE_MEMORY[symbol] = (
            alpha * new_score + (1 - alpha) * SCORE_MEMORY[symbol]
        )
    return SCORE_MEMORY[symbol]

def should_send(symbol, score, threshold=60, cooldown=900):
    now = time.time()

    if score < threshold:
        return False

    if symbol in LAST_SIGNAL:
        if now - LAST_SIGNAL[symbol] < cooldown:
            return False

    LAST_SIGNAL[symbol] = now
    return True

def entry_signal(score, rsi, trend):
    return (
        score > 70 and
        rsi < 70 and
        trend == "UP"
    )

def run():
    send_telegram("🚀 V50.2 ELITE AI BAŞLADI")

    while True:
        try:
            for symbol in COINS:
                df = get_data(symbol)

                score, rsi, trend = calculate_score(df)
                score = smooth_score(symbol, score)

                print(f"{symbol} Score:{round(score,2)} RSI:{round(rsi,2)} Trend:{trend}")

                if entry_signal(score, rsi, trend):
                    if should_send(symbol, score):
                        send_telegram(
                            f"🚀 ENTRY {symbol}\n"
                            f"Score: {round(score,2)}\n"
                            f"RSI: {round(rsi,2)}\n"
                            f"Trend: {trend}"
                        )

            time.sleep(60)

        except Exception as e:
            send_telegram(f"HATA: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    run()
