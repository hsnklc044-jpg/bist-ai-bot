import yfinance as yf


def get_support_resistance(symbol: str):

    try:

        ticker = f"{symbol}.IS"

        df = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False
        )

        if df is None or df.empty:
            return None, None

        # Son 20 mum
        recent_data = df.tail(20)

        support = float(recent_data["Low"].min())
        resistance = float(recent_data["High"].max())

        support = round(support, 2)
        resistance = round(resistance, 2)

        return support, resistance

    except Exception as e:

        print(f"Support engine error: {e}")
        return None, None