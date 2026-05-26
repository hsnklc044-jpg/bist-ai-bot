import yfinance as yf
import pandas as pd

symbol = "EREGL.IS"

print("OPTIMIZATION BASLIYOR...")

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

results = []

rsi_levels = [20, 25, 30]
exit_bars = [5, 10, 15]

for rsi_limit in rsi_levels:
    for exit_bar in exit_bars:

        trades = []

        for i in range(50, len(df)-exit_bar):

            rsi = float(df["RSI"].iloc[i])
            ma20 = float(df["MA20"].iloc[i])
            ma50 = float(df["MA50"].iloc[i])

            if rsi < rsi_limit and ma20 > ma50:

                entry = float(df["Close"].iloc[i])
                exit_price = float(df["Close"].iloc[i+exit_bar])

                change = ((exit_price - entry) / entry) * 100
                trades.append(float(change))

        if len(trades) > 0:
            winrate = len([t for t in trades if t > 0]) / len(trades) * 100
            avg = sum(trades)/len(trades)

            results.append((rsi_limit, exit_bar, round(winrate,2), round(avg,2)))

# 🔥 EN İYİYİ BUL
best = sorted(results, key=lambda x: (x[2], x[3]), reverse=True)[0]

print("---------------")
print("TUM SONUCLAR:")
for r in results:
    print(f"RSI<{r[0]} | Exit:{r[1]} → Winrate:{r[2]}% | Avg:{r[3]}%")

print("---------------")
print(f"🏆 EN IYI AYAR:")
print(f"RSI<{best[0]} | Exit:{best[1]}")
print(f"Winrate: {best[2]}% | Avg: {best[3]}%")
