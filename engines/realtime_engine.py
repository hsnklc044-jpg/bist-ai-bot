import yfinance as yf


def get_intraday_data(symbol):

    try:

        data = yf.download(
            symbol,
            period="5d",
            interval="15m",
            progress=False
        )

        return data

    except:

        return None
