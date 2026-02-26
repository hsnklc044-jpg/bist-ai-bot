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


# =============================
# RSI
# =============================
def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# =============================
# ALERT STORAGE
# =============================
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


# =============================
# STRONG LEVEL FINDER
# =============================
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


# =============================
# MAIN ENGINE
# =============================
def generate_weekly_report():

    results = []
    alarm_message = ""

    for symbol in BIST30:

        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df["Close"].dropna().astype(float)
            volume = df["Volume"]

            if len(close) < 90:
                continue

            price = close.iloc[-1]

            rsi_series = calculate_rsi(close)
            rsi = rsi_series.iloc[-1]

            avg_vol_5 = volume.tail(5).mean()
            avg_vol_20 = volume.tail(20).mean()

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

            # PROFESYONEL FİLTRE
            if (
                abs(price - support) / support < 0.03 and
                40 <= rsi <= 65 and
                avg_vol_5 > avg_vol_20 and
                rr_ratio >= 2
            ):

                results.append({
                    "Hisse": symbol,
                    "Fiyat": round(price,2),
                    "Destek": round(support,2),
                    "Direnç": round(resistance,2),
                    "Stop": round(stop,2),
                    "RSI": round(rsi,2),
                    "R/R": round(rr_ratio,2),
                    "Mesafe(%)": round(mesafe,2)
                })

                # ---- ALARM ----
                if mesafe <= 1 and not already_alerted(symbol):
                    alarm_message += (
                        f"🚨 DESTEK YAKLAŞTI\n"
                        f"{symbol.replace('.IS','')}\n"
                        f"Fiyat: {round(price,2)}\n"
                        f"Destek: {round(support,2)}\n"
                        f"Mesafe: %{round(mesafe,2)}\n"
                        f"R/R: {round(rr_ratio,2)}\n"
                        f"---\n"
                    )
                    mark_alerted(symbol)

                if price < support and not already_alerted(symbol):
                    alarm_message += (
                        f"❌ DESTEK KIRILDI\n"
                        f"{symbol.replace('.IS','')}\n"
                        f"Fiyat: {round(price,2)}\n"
                        f"---\n"
                    )
                    mark_alerted(symbol)

        except:
            continue


    df_report = pd.DataFrame(results)

    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    if df_report.empty:
        telegram_text = "⚠️ Profesyonel filtreye uygun setup yok."
    else:
        telegram_text = format_message(df_report)

    if alarm_message:
        telegram_text = alarm_message + "\n" + telegram_text

    return filename, telegram_text


def format_message(df):

    message = "🏦 PROFESYONEL SETUPLAR\n\n"

    for _, row in df.iterrows():
        message += (
            f"{row['Hisse'].replace('.IS','')}\n"
            f"Fiyat: {row['Fiyat']}\n"
            f"Destek: {row['Destek']}\n"
            f"Direnç: {row['Direnç']}\n"
            f"Stop: {row['Stop']}\n"
            f"RSI: {row['RSI']}\n"
            f"R/R: {row['R/R']}\n"
            f"Mesafe: %{row['Mesafe(%)']}\n"
            f"---\n"
        )

    return message
