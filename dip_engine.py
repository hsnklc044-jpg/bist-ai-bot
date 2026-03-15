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


def scan_dips():

    results = []

    for symbol in WATCHLIST:

        try:

            ticker = symbol + ".IS"

            data = yf.download(
                ticker,
                period="3mo",
                interval="1d",
                progress=False
            )

            if data.empty:
                continue

            close = data["Close"].dropna()

            rsi = calculate_rsi(close)

            rsi_value = rsi.iloc[-1]

            if rsi_value < 30:

                results.append({
                    "symbol": symbol,
                    "rsi": round(rsi_value,2)
                })

        except:
            continue

    if not results:
        return "Dip fırsatı bulunamadı."

    df = pd.DataFrame(results)

    df = df.sort_values(by="rsi")

    message = "💰 DIP Fırsatları\n\n"

    for _, row in df.iterrows():

        message += f"{row['symbol']} → RSI {row['rsi']}\n"

    return message