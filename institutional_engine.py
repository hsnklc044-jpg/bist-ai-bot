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

ALERT_FILE = "alerts_log.json"


# ================= RSI =================
def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ================= ALERT STORAGE =================
def load_alerts():
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_alerts(alerts):
    with open(ALERT_FILE, "w") as f:
        json.dump(alerts, f)

def already_alerted(symbol):
    alerts = load_alerts()
    today = datetime.now().strftime("%Y-%m-%d")
    return alerts.get(symbol) == today

def mark_alerted(symbol):
    alerts = load_alerts()
    today = datetime.now().strftime("%Y-%m-%d")
    alerts[symbol] = today
    save_alerts(alerts)


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

    strong = list(set([round(x,2) for x in strong]))
    return sorted(strong)


# ================= MAIN ENGINE =================
def generate_weekly_report():

    core_results = []
    watchlist_results = []
    alarm_message = ""

    for symbol in BIST30:

        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

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
            risk = price - stop
            reward = resistance - price

            if risk <= 0:
                continue

            rr_ratio = reward / risk
            mesafe = abs(price - support) / support * 100

            row_data = {
                "Hisse": symbol,
                "Fiyat": round(price,2),
                "Destek": round(support,2),
                "Direnç": round(resistance,2),
                "Stop": round(stop,2),
                "RSI": round(rsi,2),
                "R/R": round(rr_ratio,2),
                "Mesafe(%)": round(mesafe,2)
            }

            # ================= CORE =================
            if (
                mesafe < 5 and
                35 <= rsi <= 70 and
                rr_ratio >= 1.8
            ):
                core_results.append(row_data)

                if mesafe <= 1 and not already_alerted(symbol):
                    alarm_message += f"🚨 {symbol.replace('.IS','')} destek %1 içinde!\n"
                    mark_alerted(symbol)

            # ================= WATCHLIST (Genişletilmiş) =================
            elif (
                mesafe < 10 and
                25 <= rsi <= 80 and
                rr_ratio >= 1.2
            ):
                watchlist_results.append(row_data)

        except:
            continue


    core_df = pd.DataFrame(core_results)
    watch_df = pd.DataFrame(watchlist_results)

    filename = "bist_core_report.xlsx"

    with pd.ExcelWriter(filename) as writer:
        core_df.to_excel(writer, sheet_name="CORE_SETUP", index=False)
        watch_df.to_excel(writer, sheet_name="WATCHLIST", index=False)


    telegram_text = format_message(core_df, watch_df)

    if alarm_message:
        telegram_text = alarm_message + "\n" + telegram_text

    return filename, telegram_text


# ================= TELEGRAM FORMAT =================
def format_message(core_df, watch_df):

    message = "🏦 DUAL ENGINE RAPOR\n\n"

    if not core_df.empty:
        message += "🎯 CORE SETUP\n"
        for _, row in core_df.iterrows():
            message += (
                f"{row['Hisse'].replace('.IS','')} | "
                f"R/R: {row['R/R']} | "
                f"Mesafe: %{row['Mesafe(%)']}\n"
            )
        message += "\n"
    else:
        message += "🎯 CORE SETUP: Yok\n\n"

    if not watch_df.empty:
        message += "👀 WATCHLIST\n"
        for _, row in watch_df.iterrows():
            message += (
                f"{row['Hisse'].replace('.IS','')} | "
                f"R/R: {row['R/R']} | "
                f"Mesafe: %{row['Mesafe(%)']}\n"
            )
    else:
        message += "👀 WATCHLIST: Yok"

    return message
