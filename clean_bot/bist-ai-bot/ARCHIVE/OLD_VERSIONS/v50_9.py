import requests
import pandas as pd
import numpy as np

symbol = "BTCUSDT"
interval = "5m"
limit = 500

# ================= DATA =================
def get_data():
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol":symbol,"interval":interval,"limit":limit}
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "t","o","h","l","c","v","ct","qv","n","tb","tq","ig"
    ])
    df["c"] = df["c"].astype(float)
    return df

# ================= RSI =================
def rsi(series):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain/loss
    return 100 - (100/(1+rs))

# ================= BACKTEST =================
def backtest(df, score_th, tp_mult, sl_mult):

    balance = 100
    trades = 0
    wins = 0

    position = None

    rsi_val = rsi(df["c"])

    for i in range(20, len(df)):

        price = df["c"].iloc[i]
        r = rsi_val.iloc[i]

        score = 0
        if df["c"].iloc[i] > df["c"].iloc[i-5]:
            score += 50
        if 40 < r < 70:
            score += 50

        if position is None:
            if score > score_th and r < 70:
                position = {
                    "entry": price,
                    "tp": price * tp_mult,
                    "sl": price * sl_mult
                }
                trades += 1

        else:
            if price >= position["tp"]:
                balance *= 1.02
                wins += 1
                position = None

            elif price <= position["sl"]:
                balance *= 0.98
                position = None

    winrate = (wins/trades*100) if trades else 0

    return balance, trades, winrate

# ================= OPTIMIZATION =================
df = get_data()

results = []

for score_th in range(50, 80, 5):
    for tp in [1.01,1.02,1.03]:
        for sl in [0.97,0.98,0.99]:

            balance, trades, winrate = backtest(df, score_th, tp, sl)

            results.append({
                "score": score_th,
                "tp": tp,
                "sl": sl,
                "balance": balance,
                "trades": trades,
                "winrate": winrate
            })

res_df = pd.DataFrame(results)

best = res_df.sort_values("balance", ascending=False).iloc[0]

print("\n🔥 EN İYİ SONUÇ:\n")
print(best)

print("\n📊 TÜM SONUÇLAR:\n")
print(res_df.sort_values("balance", ascending=False).head(10))
