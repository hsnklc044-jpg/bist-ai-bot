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

            close = df["Close"].dropna()

            if len(close) < 20:
                results.append({"Hisse": symbol, "Durum": "Yetersiz veri"})
                continue

            close = close.astype(float)

            # MA hesaplama
            ma20 = float(close.tail(20).mean())
            ma50 = float(close.tail(50).mean()) if len(close) >= 50 else float(close.mean())

            trend = 1 if ma20 > ma50 else 0

            # Momentum
            momentum = float((close.iloc[-1] / close.iloc[-20] - 1) * 100)

            # LOG RETURN volatilite (tam scalar)
            returns = np.log(close / close.shift(1)).dropna()
            volatility = float(returns.std() * 100)

            score = float(trend * 40 + momentum * 0.8 - volatility * 0.5)

            results.append({
                "Hisse": symbol,
                "Skor": round(score, 2),
                "Volatilite(%)": round(volatility, 2),
                "Trend(0/1)": trend
            })

        except Exception as e:
            results.append({
                "Hisse": symbol,
                "Hata": str(e)
            })

    df_report = pd.DataFrame(results)

    if "Skor" in df_report.columns:
        df_report = df_report.sort_values("Skor", ascending=False)

    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    summary = (
        f"Toplam Denenen: {total_attempted}\n"
        f"Excel'e Yazılan: {len(df_report)}"
    )

    return filename, summary
