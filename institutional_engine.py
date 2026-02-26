import random

BASE_RISK = 0.01
MAX_TRADES = 3

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]


def scan_trades():

    trades = []

    for symbol in WATCHLIST:

        rr = round(random.uniform(1.5, 3.5), 2)

        if rr >= 1.8:
            trades.append({
                "symbol": symbol,
                "price": round(random.uniform(50, 200),2),
                "rr": rr,
                "score": rr
            })

    trades = sorted(trades, key=lambda x: x["score"], reverse=True)

    return {
        "regime": {
            "regime": "NORMAL",
            "risk": BASE_RISK,
            "max_trades": MAX_TRADES
        },
        "trades": trades[:MAX_TRADES]
    }
