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
                period="5d",
                interval="1h",
                progress=False
            )

            if data.empty:
                continue

            close = data["Close"]

            if close.iloc[-1] > close.iloc[-5]:

                signals.append(
                    f"📈 {ticker} momentum yükseliyor"
                )

        except Exception as e:

            print("Scanner error:", ticker, e)

    return signals


# scheduler için köprü fonksiyon

def run_ultimate_scanner():

    return ultimate_scanner()
