import pandas as pd
import numpy as np
import yfinance as yf


BIST30 = [
    "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
    "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS"
]


def generate_weekly_report():

    results = []
    total_attempted = 0

    for symbol in BIST30:

        try:
            total_attempted += 1

            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if df.empty:
                results.append({"Hisse": symbol, "Durum": "Veri çekilemedi"})
                continue

            close = df["Close"].dropna().values

            if len(close) < 20:
                results.append({"Hisse": symbol, "Durum": "Yetersiz veri"})
                continue

            # MA hesaplama
            ma20 = np.mean(close[-20:])
            ma50 = np.mean(close[-50:]) if len(close) >= 50 else np.mean(close)

            trend = 1 if ma20 > ma50 else 0

            # Momentum
            momentum = ((close[-1] / close[-20]) - 1) * 100

            # LOG RETURN volatilite (stabil yöntem)
            returns = np.diff(np.log(close))
            volatility = np.std(returns) * 100

            score = trend * 40 + momentum * 0.8 - volatility * 0.5

            results.append({
                "Hisse": symbol,
                "Skor": round(float(score), 2),
                "Volatilite(%)": round(float(volatility), 2),
                "Trend(0/1)": trend
            })

        except Exception as e:
            results.append({"Hisse": symbol, "Hata": str(e)})


    df_report = pd.DataFrame(results)

    if "Skor" in df_report.columns:
        df_report = df_report.sort_values("Skor", ascending=False)

    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    summary = (
        f"Toplam Denenen: {total_attempted}\n"
        f"Excel'e Yazılan: {len(results)}"
    )

    return filename, summary
