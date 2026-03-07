import yfinance as yf

SECTOR_SYMBOLS = {
    "BANK": "XBANK.IS",
    "INDUSTRY": "XUSIN.IS",
    "ENERGY": "XELKT.IS",
    "TECH": "XUTEK.IS"
}


def get_strong_sector():

    scores = {}

    for sector, symbol in SECTOR_SYMBOLS.items():

        try:

            data = yf.download(symbol, period="3mo", progress=False)

            ma20 = data["Close"].rolling(20).mean().iloc[-1]
            price = data["Close"].iloc[-1]

            if price > ma20:
                scores[sector] = price / ma20
            else:
                scores[sector] = 0

        except:

            scores[sector] = 0

    strongest = max(scores, key=scores.get)

    return strongest
