import yfinance as yf
from ta.momentum import RSIIndicator

BIST_LIST = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","HEKTS.IS","ISCTR.IS","KCHOL.IS",
    "KOZAA.IS","KOZAL.IS","PETKM.IS","SAHOL.IS","SISE.IS",
    "TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS","TUPRS.IS",
    "YKBNK.IS"
]


def calculate_volume_spike(data):

    volume_today = data["Volume"].iloc[-1]
    volume_avg = data["Volume"].rolling(20).mean().iloc[-1]

    if volume_avg == 0:
        return 0

    return volume_today / volume_avg


def calculate_trend(data):

    ma20 = data["Close"].rolling(20).mean().iloc[-1]
    price = data["Close"].iloc[-1]

    return price > ma20


def breakout_signal(data):

    high_20 = data["High"].rolling(20).max().iloc[-2]
    price = data["Close"].iloc[-1]

    return price > high_20


def calculate_trade_levels(data):

    support = data["Low"].rolling(20).min().iloc[-1]
    resistance = data["High"].rolling(20).max().iloc[-1]

    entry = support * 1.01
    stop = support * 0.97
    target = resistance

    risk = ((entry - stop) / entry) * 100
    reward = ((target - entry) / entry) * 100

    return {
        "support": round(support,2),
        "entry": round(entry,2),
        "stop": round(stop,2),
        "target": round(target,2),
        "risk": round(risk,2),
        "reward": round(reward,2)
    }


def calculate_score(rsi, volume_spike, trend, breakout):

    score = 0

    if rsi < 35:
        score += 30

    if volume_spike > 1.5:
        score += 25

    if trend:
        score += 20

    if breakout:
        score += 25

    return score


def scan_market():

    signals = []

    for ticker in BIST_LIST:

        try:

            data = yf.download(ticker, period="3mo", progress=False)

            if len(data) < 30:
                continue

            rsi = RSIIndicator(data["Close"]).rsi().iloc[-1]

            volume_spike = calculate_volume_spike(data)

            trend = calculate_trend(data)

            breakout = breakout_signal(data)

            score = calculate_score(rsi, volume_spike, trend, breakout)

            levels = calculate_trade_levels(data)

            signals.append({
                "ticker": ticker.replace(".IS",""),
                "score": int(score),
                "rsi": round(rsi,2),
                "volume_spike": round(volume_spike,2),
                "breakout": breakout,

                "support": levels["support"],
                "entry": levels["entry"],
                "stop": levels["stop"],
                "target": levels["target"],
                "risk": levels["risk"],
                "reward": levels["reward"]
            })

        except Exception as e:

            print("Hata:", ticker, e)

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    return signals[:5]
