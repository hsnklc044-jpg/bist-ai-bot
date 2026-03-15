import yfinance as yf
import pandas as pd
from watchlist import WATCHLIST


def get_top10():

    results = []

    for symbol in WATCHLIST:

        try:

            data = yf.download(
                symbol + ".IS",
                period="5d",
                interval="1d",
                progress=False
            )

            if data is None or data.empty:
                continue

            close = data["Close"].dropna()
            volume = data["Volume"].dropna()

            if len(close) < 2:
                continue

            today = close.iloc[-1].item()
            yesterday = close.iloc[-2].item()

            change = ((today - yesterday) / yesterday) * 100

            vol = volume.iloc[-1].item()

            results.append({
                "symbol": symbol,
                "change": round(change, 2),
                "volume": int(vol)
            })

        except Exception:
            continue

    if not results:
        return "⚠️ Veri alınamadı."

    df = pd.DataFrame(results)

    df = df.sort_values(by="change", ascending=False)

    top = df.head(10)

    message = "📊 Günün En Güçlü Hisseleri\n\n"

    for _, row in top.iterrows():

        message += f"{row['symbol']} | %{row['change']} | Hacim: {row['volume']}\n"

    return message