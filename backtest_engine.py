import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

RISK_PER_TRADE = 0.01
START_BALANCE = 100000

BIST30 = [
    "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
    "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS"
]


def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ================= BACKTEST =================

def run_backtest(years=3):

    balance = START_BALANCE
    equity_curve = [balance]
    trades = []

    for symbol in BIST30:

        df = yf.download(symbol, period=f"{years}y", interval="1d", progress=False)
        if df.empty:
            continue

        close = df["Close"]
        rsi = calculate_rsi(close)
        ema200 = close.ewm(span=200).mean()

        for i in range(250, len(df)-5):

            price = close.iloc[i]

            if price < ema200.iloc[i]:
                continue

            if rsi.iloc[i] < 50:
                continue

            support = close.iloc[i-20:i].min()
            resistance = close.iloc[i-20:i].max()

            stop = support * 0.98
            risk = price - stop
            reward = resistance - price

            if risk <= 0:
                continue

            rr = reward / risk

            if rr >= 1.8:

                risk_amount = balance * RISK_PER_TRADE
                pnl = risk_amount * rr

                balance += pnl
                equity_curve.append(balance)

                trades.append(rr)

    return equity_curve, trades


# ================= MONTE CARLO =================

def run_monte_carlo(simulations=1000):

    _, trades = run_backtest()

    if not trades:
        return None, "Trade verisi yok."

    final_balances = []
    max_dd_list = []

    for _ in range(simulations):

        shuffled = trades.copy()
        random.shuffle(shuffled)

        balance = START_BALANCE
        equity = [balance]

        for rr in shuffled:
            risk_amount = balance * RISK_PER_TRADE
            pnl = risk_amount * rr
            balance += pnl
            equity.append(balance)

        equity = np.array(equity)
        peak = np.maximum.accumulate(equity)
        drawdown = (peak - equity) / peak
        max_dd = np.max(drawdown)

        final_balances.append(balance)
        max_dd_list.append(max_dd)

    worst_dd = np.percentile(max_dd_list, 95) * 100
    avg_dd = np.mean(max_dd_list) * 100
    avg_final = np.mean(final_balances)

    # Grafik
    plt.figure(figsize=(8,4))
    plt.hist(max_dd_list, bins=40)
    plt.title("Monte Carlo Max Drawdown Distribution")
    plt.xlabel("Drawdown")
    plt.savefig("montecarlo_dd.png")
    plt.close()

    result = {
        "Simulations": simulations,
        "Avg Final Balance": round(avg_final,2),
        "Average Max DD %": round(avg_dd,2),
        "Worst 5% DD %": round(worst_dd,2)
    }

    return result, None
