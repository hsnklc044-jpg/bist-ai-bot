import pandas as pd
import numpy as np
import yfinance as yf


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
    rsi = 100 - (100 / (1 + rs))
    return rsi


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


def generate_weekly_report():

    results = []

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

            # ---- PROFESYONEL FİLTRE ----
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
                    "R/R": round(rr_ratio,2)
                })

        except:
            continue


    df_report = pd.DataFrame(results)

    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    telegram_text = format_message(df_report)

    return filename, telegram_text


def format_message(df):

    if df.empty:
        return "⚠️ Profesyonel filtreye uygun setup yok."

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
            f"---\n"
        )

    return message
