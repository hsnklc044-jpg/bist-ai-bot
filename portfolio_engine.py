import yfinance as yf
import pandas as pd
from watchlist import WATCHLIST


def calculate_rsi(data, period=14):

    delta = data.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def generate_portfolio():

    results = []

    for symbol in WATCHLIST:

        try:

            data = yf.download(
                symbol + ".IS",
                period="3mo",
                interval="1d",
                progress=False
            )

            if data.empty:
                continue

            close = data["Close"].dropna()
            volume = data["Volume"].dropna()

            price = close.iloc[-1].item()
            yesterday = close.iloc[-2].item()

            change = ((price - yesterday) / yesterday) * 100

            rsi = calculate_rsi(close)

            rsi_val = rsi.iloc[-1].item()

            avg_vol = volume[:-1].mean().item()
            today_vol = volume.iloc[-1].item()

            volume_ratio = today_vol / avg_vol

            score = change + volume_ratio

            if rsi_val < 70:
                results.append({
                    "symbol": symbol,
                    "score": score
                })

        except Exception:
            continue

    if not results:
        return "Portföy oluşturulamadı."

    df = pd.DataFrame(results)

    df = df.sort_values(by="score", ascending=False)

    top = df.head(5)

    message = "🤖 AI Portföy\n\n"

    rank = 1

    for _, row in top.iterrows():

        message += f"{rank}️⃣ {row['symbol']}\n"

        rank += 1

    return message