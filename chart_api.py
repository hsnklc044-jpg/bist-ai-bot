import yfinance as yf


def get_chart_data(symbol):

    try:

        ticker = yf.Ticker(symbol + ".IS")

        data = ticker.history(period="3mo")

        dates = data.index.strftime("%Y-%m-%d").tolist()

        prices = data["Close"].tolist()

        return dates, prices

    except:

        return [], []
