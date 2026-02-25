import pandas as pd
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

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            trend = 1 if float(df["MA20"].iloc[-1]) > float(df["MA50"].iloc[-1]) else 0

            momentum = float((df["Close"].iloc[-1] / df["Close"].iloc[-20] - 1) * 100)
            volatility = float(df["Close"].pct_change().std() * 100)

            score = float(trend * 40 + momentum * 0.8 - volatility * 0.5)

            results.append({
                "Hisse": symbol,
                "Skor": round(score,2),
                "Volatilite(%)": round(volatility,2)
            })

        except Exception:
            continue


    df_report = pd.DataFrame(results).sort_values("Skor", ascending=False)

    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    summary = f"Toplam İncelenen: {len(results)}"

    return filename, summary
