import yfinance as yf
import pandas as pd
import numpy as np

# ================= CONFIG =================
SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]

ACCOUNT_SIZE = 100000
RISK = 0.02

LOOKBACK_DAYS = 60

# BACKTEST TF
TF_ENTRY = "5m"
TF_TREND = "15m"

# PARAM GRID
ATR_SL_RANGE = [0.8, 1.0, 1.2]
ATR_TP_RANGE = [1.5, 2.0, 2.5]
TIME_RANGE = [120, 180, 240]

# ================= DATA =================
def get_data(sym, tf):
    df = yf.download(sym, period=f"{LOOKBACK_DAYS}d", interval=tf, progress=False)

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

# ================= TREND FILTER =================
def trend_filter(df):
    ma = df["Close"].rolling(20).mean()
    return df["Close"] > ma  # True = bullish

# ================= BACKTEST =================
def run_test(params):
    ATR_SL, ATR_TP, MAX_DURATION = params

    total_pnl = 0
    trades = []
    equity = []

    for sym in SYMBOLS:

        df_5m = get_data(sym, TF_ENTRY)
        df_15m = get_data(sym, TF_TREND)

        if df_5m is None or df_15m is None:
            continue

        df_5m["ATR"] = atr(df_5m)
        df_15m["trend"] = trend_filter(df_15m)

        df_5m = df_5m.dropna()

        position = None
        entry_time = None

        for i in range(len(df_5m)):

            row = df_5m.iloc[i]
            now = df_5m.index[i]

            # trend align (son 15m bar)
            trend_row = df_15m[df_15m.index <= now].iloc[-1]
            bullish = trend_row["trend"]

            sig = signal(row)
            price = row["Close"]
            atr_val = row["ATR"]

            # ===== EXIT =====
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
                        reason="SL"; exit_flag=True
                    elif price >= entry+tp:
                        reason="TP"; exit_flag=True
                else:
                    if price >= entry+sl:
                        reason="SL"; exit_flag=True
                    elif price <= entry-tp:
                        reason="TP"; exit_flag=True

                if (now - entry_time).seconds > MAX_DURATION:
                    reason="TIME"; exit_flag=True

                if exit_flag:
                    size = (ACCOUNT_SIZE*RISK)/entry
                    pnl_total = pnl * size

                    total_pnl += pnl_total
                    trades.append(pnl_total)
                    equity.append(total_pnl)

                    position = None
                    continue

            # ===== ENTRY =====
            if not position and sig:

                # trend filter
                if sig=="LONG" and not bullish:
                    continue
                if sig=="SHORT" and bullish:
                    continue

                position = {
                    "side": sig,
                    "entry": price,
                    "atr": atr_val
                }
                entry_time = now

    # ===== METRICS =====
    if len(trades) == 0:
        return None

    trades = np.array(trades)
    equity = np.array(equity)

    winrate = (trades>0).sum()/len(trades)
    total = trades.sum()
    avg = trades.mean()

    peak = np.maximum.accumulate(equity)
    dd = (equity - peak).min()

    return {
        "params": params,
        "trades": len(trades),
        "winrate": winrate,
        "pnl": total,
        "avg": avg,
        "max_dd": dd
    }

# ================= OPTIMIZER =================
results = []

print("🚀 PRO MULTI-TF BACKTEST STARTED")

for sl in ATR_SL_RANGE:
    for tp in ATR_TP_RANGE:
        for t in TIME_RANGE:

            res = run_test((sl,tp,t))

            if res:
                results.append(res)
                print(f"SL={sl} TP={tp} T={t} -> PnL={res['pnl']:.2f}")

# ================= RESULTS =================
df = pd.DataFrame(results)

df = df.sort_values(by="pnl", ascending=False)

print("\n🏆 BEST:")
print(df.head(1))

print("\n📊 TOP 5:")
print(df.head(5))