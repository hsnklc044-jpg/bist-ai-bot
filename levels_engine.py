import yfinance as yf


def get_levels(symbol):

    try:

        data = yf.download(
            symbol + ".IS",
            period="6mo",
            interval="1d",
            progress=False
        )

        if data.empty:
            return "Veri bulunamadı."

        close = data["Close"].dropna()

        price = close.iloc[-1].item()

        recent = close.tail(60)

        support = recent.min().item()
        resistance = recent.max().item()

        message = (
            f"📊 Destek / Direnç Analizi\n\n"
            f"Hisse: {symbol}\n\n"
            f"Destek: {round(support,2)}\n"
            f"Direnç: {round(resistance,2)}\n"
            f"Güncel Fiyat: {round(price,2)}"
        )

        return message

    except Exception as e:

        return f"Analiz hatası: {str(e)}"