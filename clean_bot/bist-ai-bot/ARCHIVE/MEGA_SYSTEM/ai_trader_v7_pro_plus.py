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

# 🧠 SEKTÖR (BANKA FİLTRESİ)
bank_symbols = ["YKBNK","AKBNK","GARAN","ISCTR"]

# 💰 SERMAYE
capital = 100000
initial_capital = capital

active_trades = []
wins = 0
losses = 0

# 🔥 AYARLAR
RISK_PER_TRADE = 0.02
MAX_DRAWDOWN = 0.10
MAX_TRADES = 3

TRAIL_TRIGGER = 0.02
TRAIL_GAP = 0.015

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

print("AI TRADER V7 PRO+ CALISIYOR...")
send("💼 AI TRADER V7 PRO+ AKTİF")

while True:
    try:
        # 📉 DRAWDOWN kontrol
        dd = (initial_capital - capital) / initial_capital
        if dd >= MAX_DRAWDOWN:
            send("⛔ MAX DRAWDOWN AŞILDI - SİSTEM DURDU")
            break

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

            if score >= 5:
                candidates.append((symbol, price, rsi_val, score))

        # 🚀 TRADE AÇ
        for c in sorted(candidates, key=lambda x: x[3], reverse=True):

            if len(active_trades) >= MAX_TRADES:
                break

            # ❗ aynı hisse açık mı
            if any(t["symbol"] == c[0] for t in active_trades):
                continue

            # 🧠 SEKTÖR FİLTRESİ (BANKA)
            if c[0] in bank_symbols:
                if sum(1 for t in active_trades if t["symbol"] in bank_symbols) >= 1:
                    continue

            price = c[1]

            sl = price * 0.97
            risk_amount = capital * RISK_PER_TRADE
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)
            tp = round(price * 1.05, 2)

            trade = {
                "symbol": c[0],
                "entry": price,
                "tp": tp,
                "sl": sl,
                "lot": lot,
                "max_price": price
            }

            active_trades.append(trade)

            send(f"🚀 TRADE\n{trade['symbol']}\nEntry:{round(price,2)}\nLot:{lot}\nTP:{tp} SL:{round(sl,2)}")

        # 🔄 TAKİP
        for trade in active_trades[:]:
            df = get_data(trade["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price > trade["max_price"]:
                trade["max_price"] = price

            # 🔄 TRAILING STOP
            if trade["max_price"] >= trade["entry"] * (1 + TRAIL_TRIGGER):
                new_sl = trade["max_price"] * (1 - TRAIL_GAP)
                if new_sl > trade["sl"]:
                    trade["sl"] = new_sl
                    send(f"🔄 SL Güncellendi {trade['symbol']} → {round(trade['sl'],2)}")

            # 🟢 TP
            if price >= trade["tp"]:
                profit = (trade["tp"] - trade["entry"]) * trade["lot"]
                capital += profit
                wins += 1
                send(f"🟢 TP {trade['symbol']} +{round(profit,2)} TL")
                active_trades.remove(trade)

            # 🔴 SL
            elif price <= trade["sl"]:
                loss = (trade["entry"] - trade["sl"]) * trade["lot"]
                capital -= loss
                losses += 1
                send(f"🔴 SL {trade['symbol']} -{round(loss,2)} TL")
                active_trades.remove(trade)

        # 📊 RAPOR
        total = wins + losses
        if total > 0:
            winrate = round((wins / total) * 100, 2)
            send(f"📊 DURUM\nBakiye:{round(capital,2)} TL\nWin:{wins} Loss:{losses}\nBaşarı:{winrate}%")

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
