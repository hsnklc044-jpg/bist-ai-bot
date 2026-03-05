import yfinance as yf


def ultimate_scanner():

    tickers = [
        "ASELS.IS",
        "THYAO.IS",
        "EREGL.IS",
        "SISE.IS",
        "KCHOL.IS"
    ]

    signals = []

    for ticker in tickers:

        try:

            data = yf.download(
                ticker,
                period="1d",
                interval="1h",
                progress=False
            )

            if data.empty:
                continue

            last_price = data["Close"].iloc[-1]

            signals.append(
                f"📈 TEST SIGNAL\n{ticker}\nFiyat: {round(float(last_price),2)}"
            )

        except Exception as e:

            print("Scanner error:", ticker, e)

    return signals


# scheduler için köprü fonksiyon

def run_ultimate_scanner():

    return ultimate_scanner()
