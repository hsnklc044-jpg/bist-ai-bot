import requests
import time
import yfinance as yf
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

active_trades = []
wins = 0
losses = 0

RISK_PERCENT = 0.03  # %3 risk
TRAIL_TRIGGER = 0.02 # %2 kar sonrası trailing
TRAIL_GAP = 0.015    # %1.5 trailing mesafe

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="5d", interval="15m", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

def rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

print("AI TRADER V5 CALISIYOR...")
send("🧠 AI TRADER V5 AKTİF")

while True:
    try:
        candidates = []

        # 📊 TARAYICI
        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1])
            rsi_val = float(df["RSI"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])

            score = 0

            if rsi_val < 30: score += 4
            elif rsi_val < 40: score += 3
            elif rsi_val < 50: score += 2

            if price > ma20: score += 2
            if price > ma50: score += 1

            tp = round(price * 1.05, 2)
            sl = round(price * (1 - RISK_PERCENT), 2)

            if score >= 4:
                candidates.append((symbol, price, rsi_val, score, tp, sl))

        # 🚀 YENİ TRADE
        if candidates:
            best = sorted(candidates, key=lambda x: x[3], reverse=True)[0]

            already_open = any(t["symbol"] == best[0] for t in active_trades)

            if not already_open:
                trade = {
                    "symbol": best[0],
                    "entry": best[1],
                    "tp": best[4],
                    "sl": best[5],
                    "max_price": best[1]
                }
                active_trades.append(trade)

                send(f"🚀 TRADE AÇILDI\n\n{trade['symbol']}\nEntry:{trade['entry']}\nTP:{trade['tp']} SL:{trade['sl']}")

        # 🔄 TAKİP + TRAILING
        for trade in active_trades[:]:
            df = get_data(trade["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            # 📈 MAX PRICE güncelle
            if price > trade["max_price"]:
                trade["max_price"] = price

            # 🔥 TRAILING AKTİF
            if trade["max_price"] >= trade["entry"] * (1 + TRAIL_TRIGGER):
                new_sl = round(trade["max_price"] * (1 - TRAIL_GAP), 2)

                if new_sl > trade["sl"]:
                    trade["sl"] = new_sl
                    send(f"🔄 TRAILING SL GÜNCELLENDİ\n{trade['symbol']} SL:{trade['sl']}")

            # 🟢 TP
            if price >= trade["tp"]:
                wins += 1
                send(f"🟢 TP HIT\n{trade['symbol']} +5%")
                active_trades.remove(trade)

            # 🔴 SL
            elif price <= trade["sl"]:
                losses += 1
                send(f"🔴 SL HIT\n{trade['symbol']}")
                active_trades.remove(trade)

        # 📊 RAPOR
        total = wins + losses
        if total > 0:
            winrate = round((wins / total) * 100, 2)
            send(f"📊 PERFORMANS\nWin:{wins} Loss:{losses}\nBaşarı:{winrate}%")

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
