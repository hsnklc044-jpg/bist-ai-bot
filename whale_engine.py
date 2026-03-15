import yfinance as yf


def detect_whale(symbol):

    try:

        data = yf.download(symbol, period="1mo")

        if data.empty:
            return False

        volume = data["Volume"]

        avg_volume = volume.mean()

        last_volume = volume.iloc[-1]

        if last_volume > avg_volume * 2:

            return True

        else:

            return False

    except:

        return False
