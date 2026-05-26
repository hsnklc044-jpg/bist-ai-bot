import requests
import time
import yfinance as yf
import pandas as pd

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

strategy_score = {
    "low_rsi": 0,
    "mid_rsi": 0
}

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="5d", interval="15m", progress=False)
        if df.empty:
            return None
        return df
    except:
        return None

def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

print("AI TRADER V2 CALISIYOR...")

while True:
    try:
        trades = []

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = calculate_rsi(df)
            df["MA20"] = df["Close"].rolling(20).mean()

            last = df.iloc[-1]

            price = float(last["Close"])
            rsi = float(last["RSI"]) if not pd.isna(last["RSI"]) else 50
            ma20 = float(last["MA20"]) if not pd.isna(last["MA20"]) else price

            # 🧠 STRATEJI SECIMI (LEARNING)
            if strategy_score["low_rsi"] == 0 and strategy_score["mid_rsi"] == 0:
                use_low_rsi = True
            else:
                use_low_rsi = strategy_score["low_rsi"] > strategy_score["mid_rsi"]

            signal = None
            strat = ""

            # 🎯 STRATEJI 1
            if use_low_rsi:
                if rsi < 30 and price > ma20:
                    signal = "BUY"
                    strat = "low_rsi"

            # 🎯 STRATEJI 2
            else:
                if 40 < rsi < 60 and price > ma20:
                    signal = "BUY"
                    strat = "mid_rsi"

            if signal == "BUY":
                tp = round(price * 1.04, 2)
                sl = round(price * 0.97, 2)

                trades.append({
                    "symbol": symbol,
                    "price": price,
                    "tp": tp,
                    "sl": sl,
                    "strat": strat,
                    "rsi": round(rsi,2)
                })

        if len(trades) > 0:
            msg = "🧠 AI TRADELER:\n\n"

            for t in trades:
                msg += f"🚀 {t['symbol']}\n"
                msg += f"Entry: {round(t['price'],2)}\n"
                msg += f"RSI: {t['rsi']}\n"
                msg += f"TP: {t['tp']} | SL: {t['sl']}\n"
                msg += f"Strat: {t['strat']}\n\n"

            send(msg)
        else:
            send("⚖️ Uygun trade yok")

    except Exception as e:
        print("HATA:", e)

    time.sleep(60)
