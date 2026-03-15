import yfinance as yf


def get_support(symbol):

    try:

        data = yf.download(
            symbol + ".IS",
            period="6mo",
            interval="1d",
            progress=False
        )

        if data.empty:
            return "Veri bulunamadı."

        lows = data["Low"].dropna()

        support = lows.min().item()

        current_price = data["Close"].iloc[-1].item()

        message = (
            f"📉 Destek Analizi\n\n"
            f"Hisse: {symbol}\n"
            f"Güncel Fiyat: {round(current_price,2)}\n"
            f"Güçlü Destek: {round(support,2)}"
        )

        return message

    except Exception:

        return "Analiz yapılamadı."