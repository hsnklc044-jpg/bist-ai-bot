import yfinance as yf
import pandas as pd
import numpy as np
import json

# ================= CONFIG =================
SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]

ACCOUNT_SIZE = 100000
RISK = 0.02

TF = "5m"
LOOKBACK_DAYS = 60
TRAIN_SPLIT = 0.7

TOP_N = 2  # 🔥 en iyi kaç sembol

ATR_SL_RANGE = [0.6, 0.8, 1.0]
ATR_TP_RANGE = [1.5, 2.0, 2.5]
TIME_RANGE = [600, 900, 1200]

# ================= DATA =================
def get_data(sym):
    df = yf.download(sym, period=f"{LOOKBACK_DAYS}d", interval=TF, progress=False)
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

# ================= ATR =================
def atr(df, p=14):
    tr = pd.concat([
        df['High']-df['Low'],
        (df['High']-df['Close'].shift()).abs(),
        (df['Low']-df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(p).mean()

# ================= SIGNAL =================
def signal(row):
    c,h,l = row["Close"], row["High"], row["Low"]
    rng = (h-l)+1e-9
    if (c-l)/rng > 0.3:
        return "LONG"
    elif (h-c)/rng > 0.3:
        return "SHORT"
    return None

# ================= BACKTEST =================
def run(df, params):
    ATR_SL, ATR_TP, MAX_DURATION = params

    total = 0
    trades = []

    position = None
    entry_time = None

    for i in range(len(df)):
        row = df.iloc[i]
        now = df.index[i]

        sig = signal(row)
        price = row["Close"]
        atr_v = row["ATR"]

        # EXIT
        if position:
            entry = position["entry"]
            side = position["side"]
            atr_e = position["atr"]

            pnl = (price-entry) if side=="LONG" else (entry-price)

            sl = atr_e * ATR_SL
            tp = atr_e * ATR_TP

            exit_flag = False

            if side=="LONG":
                if price <= entry-sl:
                    exit_flag=True
                elif price >= entry+tp:
                    exit_flag=True
            else:
                if price >= entry+sl:
                    exit_flag=True
                elif price <= entry-tp:
                    exit_flag=True

            if (now - entry_time).seconds > MAX_DURATION:
                exit_flag=True

            if exit_flag:
                size = (ACCOUNT_SIZE*RISK)/entry
                pnl_total = pnl * size
                total += pnl_total
                trades.append(pnl_total)
                position=None
                continue

        # ENTRY
        if not position and sig:
            position = {"side":sig,"entry":price,"atr":atr_v}
            entry_time = now

    return total, trades

# ================= WALK FORWARD =================
def evaluate(sym):
    df = get_data(sym)
    if df is None:
        return None

    df["ATR"] = atr(df)
    df = df.dropna()

    split = int(len(df)*TRAIN_SPLIT)

    train = df.iloc[:split]
    test = df.iloc[split:]

    best = None
    best_score = -999999

    # optimize
    for sl in ATR_SL_RANGE:
        for tp in ATR_TP_RANGE:
            for t in TIME_RANGE:

                pnl,_ = run(train,(sl,tp,t))

                if pnl > best_score:
                    best_score = pnl
                    best = (sl,tp,t)

    # validate
    test_pnl, trades = run(test,best)

    return {
        "symbol": sym,
        "params": best,
        "train_pnl": best_score,
        "test_pnl": test_pnl,
        "trades": len(trades)
    }

# ================= MAIN =================
print("🚀 PORTFOLIO RANKING STARTED")

results = []

for sym in SYMBOLS:
    res = evaluate(sym)
    if res:
        results.append(res)
        print(res)

df = pd.DataFrame(results)

# 🔥 sadece pozitif edge
df = df[df["test_pnl"] > 0]

# 🔥 ranking
df = df.sort_values(by="test_pnl", ascending=False)

top = df.head(TOP_N)

print("\n🏆 TOP SYMBOLS:")
print(top)

# ================= SAVE =================
output = {
    "symbols": list(top["symbol"]),
    "params": list(top["params"])[0] if len(top)>0 else None
}

with open("portfolio_config.json","w") as f:
    json.dump(output,f,indent=4)

print("\n✅ portfolio_config.json oluşturuldu")