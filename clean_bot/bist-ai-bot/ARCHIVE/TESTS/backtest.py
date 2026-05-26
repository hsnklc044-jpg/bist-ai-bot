import yfinance as yf
import pandas as pd

symbol = "EREGL.IS"

print("BACKTEST BASLIYOR...")

df = yf.download(symbol, period="6mo", interval="1h")

def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df["RSI"] = calculate_rsi(df)

df["MA20"] = df["Close"].rolling(20).mean()
df["MA50"] = df["Close"].rolling(50).mean()

trades = []

for i in range(50, len(df)-10):

    rsi = float(df["RSI"].iloc[i])
    ma20 = float(df["MA20"].iloc[i])
    ma50 = float(df["MA50"].iloc[i])

    if rsi < 30 and ma20 > ma50:

        entry = float(df["Close"].iloc[i])
        exit_price = float(df["Close"].iloc[i+10])

        change = ((exit_price - entry) / entry) * 100

        trades.append(float(change))

# 🔥 garanti float listesi
trades = [float(x) for x in trades]

total = len(trades)
wins = len([t for t in trades if t > 0])
loss = len([t for t in trades if t <= 0])

winrate = (wins / total * 100) if total > 0 else 0
avg = sum(trades)/total if total > 0 else 0

print("---------------")
print(f"Toplam işlem: {total}")
print(f"Kazanan: {wins}")
print(f"Kaybeden: {loss}")
print(f"Başarı oranı: {round(winrate,2)}%")
print(f"Ortalama getiri: {round(avg,2)}%")
