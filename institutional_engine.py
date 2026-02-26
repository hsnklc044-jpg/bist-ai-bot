import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
from datetime import datetime

BIST30 = [
    "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
    "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS"
]

BALANCE_FILE = "balance.json"
ALERT_FILE = "alerts_log.json"

RISK_PER_TRADE = 0.01
MAX_POSITIONS = 5
MAX_DAILY_RISK = 0.03


# ================= BALANCE =================
def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    return {"balance": 100000}

def save_balance(amount):
    with open(BALANCE_FILE, "w") as f:
        json.dump({"balance": amount}, f)


# ================= RSI =================
def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ================= STRONG LEVELS =================
def find_strong_levels(close):
    prices = close.tail(90).values
    levels = []

    for i in range(2, len(prices)-2):
        if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
            levels.append(prices[i])
        if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
            levels.append(prices[i])

    strong = []
    for lvl in levels:
        cluster = [x for x in levels if abs(x - lvl) / lvl < 0.01]
        if len(cluster) >= 2:
            strong.append(np.mean(cluster))

    return sorted(list(set([round(x,2) for x in strong])))


# ================= MAIN ENGINE =================
def generate_weekly_report():

    balance_data = load_balance()
    balance = balance_data["balance"]
    risk_amount = balance * RISK_PER_TRADE

    daily_risk_used = 0
    position_count = 0

    results = []

    for symbol in BIST30:

        if position_count >= MAX_POSITIONS:
            break

        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df.empty:
                continue

            close = df["Close"].dropna().astype(float)

            if len(close) < 90:
                continue

            price = float(close.iloc[-1])
            rsi = float(calculate_rsi(close).iloc[-1])

            strong_levels = find_strong_levels(close)

            supports = [lvl for lvl in strong_levels if lvl < price]
            resistances = [lvl for lvl in strong_levels if lvl > price]

            if not supports or not resistances:
                continue

            support = max(supports)
            resistance = min(resistances)

            stop = support * 0.98
            risk_per_share = price - stop

            if risk_per_share <= 0:
                continue

            rr_ratio = (resistance - price) / risk_per_share
            mesafe = abs(price - support) / support * 100

            # CORE filtre
            if mesafe < 5 and 35 <= rsi <= 70 and rr_ratio >= 1.8:

                lot = int(risk_amount / risk_per_share)

                if daily_risk_used + RISK_PER_TRADE > MAX_DAILY_RISK:
                    break

                results.append({
                    "Hisse": symbol,
                    "Fiyat": round(price,2),
                    "Stop": round(stop,2),
                    "R/R": round(rr_ratio,2),
                    "Lot": lot,
                    "RiskTL": int(risk_amount)
                })

                daily_risk_used += RISK_PER_TRADE
                position_count += 1

        except:
            continue

    df_report = pd.DataFrame(results)
    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    telegram_text = format_message(df_report, balance, daily_risk_used, position_count)

    return filename, telegram_text


def format_message(df, balance, daily_risk, pos_count):

    message = f"🏦 RİSK MOTORU RAPOR\n\nPortföy: {balance} TL\n"

    if df.empty:
        message += "Uygun CORE setup yok."
    else:
        for _, row in df.iterrows():
            message += (
                f"\n{row['Hisse'].replace('.IS','')}\n"
                f"Fiyat: {row['Fiyat']}\n"
                f"Stop: {row['Stop']}\n"
                f"R/R: {row['R/R']}\n"
                f"Lot: {row['Lot']}\n"
                f"Risk: {row['RiskTL']} TL\n"
            )

    message += f"\nToplam Günlük Risk: %{daily_risk*100}\n"
    message += f"Açık Pozisyon: {pos_count}/{MAX_POSITIONS}"

    return message
