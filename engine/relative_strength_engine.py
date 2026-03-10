import yfinance as yf
import pandas as pd


INDEX_SYMBOL = "XU100.IS"
LOOKBACK_PERIOD = "3mo"


def download_index():

    try:

        df = yf.download(
            INDEX_SYMBOL,
            period=LOOKBACK_PERIOD,
            interval="1d",
            progress=False
        )

        if df is None or df.empty:
            return None

        df.dropna(inplace=True)

        return df

    except Exception as e:

        print("Index verisi indirilemedi:", e)
        return None


def calculate_return(df):

    try:

        start = df["Close"].iloc[-20]
        end = df["Close"].iloc[-1]

        return (end - start) / start

    except:
        return 0


def relative_strength_vs_index(stock_df):

    index_df = download_index()

    if index_df is None:
        return False

    stock_return = calculate_return(stock_df)
    index_return = calculate_return(index_df)

    if stock_return > index_return:

        return {
            "stronger_than_index": True,
            "stock_return": round(stock_return, 4),
            "index_return": round(index_return, 4)
        }

    return {
        "stronger_than_index": False,
        "stock_return": round(stock_return, 4),
        "index_return": round(index_return, 4)
    }
