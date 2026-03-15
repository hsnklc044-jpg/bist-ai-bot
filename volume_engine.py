import yfinance as yf
from watchlist import WATCHLIST


def volume_scan():

    results = []

    for symbol in WATCHLIST:

        try:

            ticker = symbol + ".IS"

            df = yf.download(
                ticker,
                period="10d",
                interval="1d",
                progress=False
            )

            if df.empty:
                continue

            volume = df["Volume"]

            today_vol = volume.iloc[-1]
            avg_vol = volume[:-1].mean()

            ratio = today_vol / avg_vol

            if ratio > 2:

                results.append(
                    f"{symbol} → Hacim {ratio:.2f}x"
                )

        except:
            continue

    if not results:
        return "Hacim patlaması bulunamadı."

    message = "🔥 Hacim Patlaması\n\n"

    for r in results[:5]:
        message += r + "\n"

    return message