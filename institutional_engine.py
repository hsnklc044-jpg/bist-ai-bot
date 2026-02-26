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

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df["Close"].dropna()

            if len(close) < 50:
                results.append({"Hisse": symbol, "Durum": "Yetersiz veri"})
                continue

            close = close.astype(float)

            price = close.iloc[-1]

            ma20 = close.tail(20).mean()
            ma50 = close.tail(50).mean()

            swing_low = close.tail(14).min()

            trend = 1 if ma20 > ma50 else 0

            momentum = (price / close.iloc[-20] - 1) * 100

            returns = np.log(close / close.shift(1)).dropna()
            volatility = returns.std() * 100

            score = trend * 40 + momentum * 0.8 - volatility * 0.5

            # Destek = MA20 ile Swing Low arasında düşük olan
            support = min(ma20, swing_low)

            # Stop = destek altı %2
            stop = support * 0.98

            results.append({
                "Hisse": symbol,
                "Fiyat": round(price, 2),
                "Skor": round(score, 2),
                "Volatilite(%)": round(volatility, 2),
                "Destek": round(support, 2),
                "Stop": round(stop, 2),
                "Trend": trend
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
