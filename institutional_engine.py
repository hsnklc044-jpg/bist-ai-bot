import pandas as pd
import numpy as np
import yfinance as yf


BIST30 = [
    "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
    "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS"
]


def generate_weekly_report():

    results = []

    for symbol in BIST30:

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if df.empty or len(df) < 60:
                continue

            close = df["Close"].values

            ma20 = np.mean(close[-20:])
            ma50 = np.mean(close[-50:])

            trend = 1 if ma20 > ma50 else 0

            momentum = ((close[-1] / close[-20]) - 1) * 100
            volatility = np.std(np.diff(close) / close[:-1]) * 100

            score = trend * 40 + momentum * 0.8 - volatility * 0.5

            results.append({
                "Hisse": symbol,
                "Skor": round(float(score), 2),
                "Volatilite(%)": round(float(volatility), 2)
            })

        except Exception:
            continue


    if len(results) == 0:
        df_report = pd.DataFrame([{"Durum": "Uygun veri yok"}])
    else:
        df_report = pd.DataFrame(results)
        df_report = df_report.sort_values("Skor", ascending=False)


    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    summary = f"Toplam İncelenen: {len(results)}"

    return filename, summary
