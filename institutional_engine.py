import pandas as pd
import numpy as np
import yfinance as yf


BIST30 = [
    "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
    "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS"
]


def find_strong_levels(close):

    prices = close.tail(60).values

    levels = []

    # Lokal dip ve tepeleri bul
    for i in range(2, len(prices)-2):

        if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
            levels.append(prices[i])

        if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
            levels.append(prices[i])

    # Benzer seviyeleri grupla (±1%)
    strong_levels = []

    for level in levels:
        cluster = [x for x in levels if abs(x - level) / level < 0.01]
        if len(cluster) >= 2:
            strong_levels.append(np.mean(cluster))

    strong_levels = list(set([round(x,2) for x in strong_levels]))

    return sorted(strong_levels)


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

            if len(close) < 60:
                continue

            price = close.iloc[-1]

            strong_levels = find_strong_levels(close)

            supports = [lvl for lvl in strong_levels if lvl < price]
            resistances = [lvl for lvl in strong_levels if lvl > price]

            support = max(supports) if supports else None
            resistance = min(resistances) if resistances else None

            if support:
                stop = support * 0.98
            else:
                stop = None

            results.append({
                "Hisse": symbol,
                "Fiyat": round(price,2),
                "Güçlü Destek": support,
                "Güçlü Direnç": resistance,
                "Stop": round(stop,2) if stop else None
            })

        except:
            continue


    df_report = pd.DataFrame(results)

    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    telegram_text = format_telegram_message(df_report)

    return filename, telegram_text


def format_telegram_message(df):

    if df.empty:
        return "⚠️ Veri bulunamadı."

    message = "📊 GÜÇLÜ SEVİYELER\n\n"

    for _, row in df.iterrows():
        message += (
            f"{row['Hisse'].replace('.IS','')}\n"
            f"Fiyat: {row['Fiyat']}\n"
            f"Destek: {row['Güçlü Destek']}\n"
            f"Direnç: {row['Güçlü Direnç']}\n"
            f"Stop: {row['Stop']}\n"
            f"---\n"
        )

    return message
