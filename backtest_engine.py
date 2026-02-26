import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

            # 🔥 Trend filtresi
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

    return analyze_results(equity_curve, trades)


def analyze_results(equity_curve, trades):

    returns = np.diff(equity_curve) / equity_curve[:-1]

    sharpe = 0
    if np.std(returns) != 0:
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)

    peak = np.maximum.accumulate(equity_curve)
    drawdown = (peak - equity_curve) / peak
    max_dd = np.max(drawdown)

    win_rate = sum(1 for t in trades if t > 0) / len(trades) if trades else 0
    profit_factor = (
        sum(t for t in trades if t > 0) /
        abs(sum(t for t in trades if t < 0))
        if any(t < 0 for t in trades) else 0
    )

    plt.figure(figsize=(8,4))
    plt.plot(equity_curve)
    plt.title("Trend Filtered Backtest Equity")
    plt.grid(True)
    plt.savefig("backtest_equity.png")
    plt.close()

    return {
        "Final Balance": round(equity_curve[-1],2),
        "Sharpe Ratio": round(sharpe,2),
        "Max Drawdown %": round(max_dd*100,2),
        "Win Rate %": round(win_rate*100,2),
        "Profit Factor": round(profit_factor,2),
        "Total Trades": len(trades)
    }
