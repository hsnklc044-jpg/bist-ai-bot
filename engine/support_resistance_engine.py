import yfinance as yf


def get_support_resistance(symbol):

    try:

        ticker = f"{symbol}.IS"

        df = yf.download(ticker, period="6mo", interval="1d")

        if df.empty:
            return "Veri bulunamadı."

        support = df["Low"].min()
        resistance = df["High"].max()
        price = df["Close"].iloc[-1]

        text = f"""
📊 {symbol}

Fiyat: {round(price,2)}

🟢 Destek: {round(support,2)}
🔴 Direnç: {round(resistance,2)}
"""

        return text

    except Exception as e:

        return f"Hata: {str(e)}"
