# RSI hesaplama
delta = df["Close"].diff()

gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

rs = avg_gain / avg_loss
df["RSI"] = 100 - (100 / (1 + rs))

# Ortalama hacim
df["VOL_AVG20"] = df["Volume"].rolling(window=20).mean()

df = df.dropna()
