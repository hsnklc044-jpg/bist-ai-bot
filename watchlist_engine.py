import yfinance as yf
import pandas as pd
from watchlist import WATCHLIST


def generate_watchlist():

    results = []

    for symbol in WATCHLIST:

        try:

            ticker = symbol + ".IS"

            df = yf.download(
                ticker,
                period="1mo",
                interval="1d",
                progress=False
            )

            if df.empty:
                continue

            close = df["Close"].dropna()
            volume = df["Volume"].dropna()

            price = close.iloc[-1].item()
            week_ago = close.iloc[-5].item()

            momentum = ((price - week_ago) / week_ago) * 100

            avg_volume = volume[:-1].mean()
            today_volume = volume.iloc[-1].item()

            volume_ratio = today_volume / avg_volume

            score = momentum + volume_ratio

            results.append({
                "symbol": symbol,
                "score": score
            })

        except:
            continue

    if not results:
        return "Watchlist oluşturulamadı."

    df = pd.DataFrame(results)

    df = df.sort_values("score", ascending=False)

    top = df.head(5)

    message = "📊 Bugünün En Güçlü Hisseleri\n\n"

    for i, row in top.iterrows():
        message += f"{row['symbol']}\n"

    return message