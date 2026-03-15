import yfinance as yf
import pandas as pd
from watchlist import WATCHLIST


def fast_scan():

    results = []

    for symbol in WATCHLIST:

        try:

            data = yf.download(
                symbol + ".IS",
                period="2d",
                interval="1d",
                progress=False
            )

            if data is None or data.empty:
                continue

            close = data["Close"].dropna()

            if len(close) < 2:
                continue

            today = close.iloc[-1].item()
            yesterday = close.iloc[-2].item()

            change = ((today - yesterday) / yesterday) * 100

            results.append({
                "symbol": symbol,
                "change": round(change, 2)
            })

        except Exception:
            continue

    if not results:
        return "⚠️ Veri alınamadı."

    df = pd.DataFrame(results)

    df = df.sort_values(by="change", ascending=False)

    top = df.head(5)

    message = "⚡ Momentum Tarama\n\n"

    for _, row in top.iterrows():
        message += f"{row['symbol']} | %{row['change']}\n"

    return message