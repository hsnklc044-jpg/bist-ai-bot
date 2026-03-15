import yfinance as yf

TICKERS = [
"THYAO.IS","EREGL.IS","TUPRS.IS","ASELS.IS","KCHOL.IS",
"SAHOL.IS","BIMAS.IS","AKBNK.IS","GARAN.IS","ISCTR.IS",
"YKBNK.IS","PGSUS.IS","SASA.IS","HEKTS.IS","KRDMD.IS"
]


def market_heatmap():

    stock_scores = []

    for ticker in TICKERS:

        try:

            data = yf.download(ticker, period="5d", interval="1d", progress=False)

            if len(data) < 2:
                continue

            close_today = float(data["Close"].iloc[-1])
            close_yesterday = float(data["Close"].iloc[-2])

            change = ((close_today - close_yesterday) / close_yesterday) * 100

            stock_scores.append({
                "ticker": ticker,
                "score": round(change,2)
            })

        except:
            pass

    stock_scores = sorted(stock_scores, key=lambda x: x["score"], reverse=True)

    return stock_scores
