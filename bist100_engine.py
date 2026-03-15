import yfinance as yf
import time

BIST100 = [

"AEFES","AKBNK","AKSA","AKSEN","ALARK","ALBRK","ARCLK","ASELS","BIMAS","BRISA",
"CIMSA","DOAS","ECILC","EKGYO","ENJSA","EREGL","FROTO","GARAN","GESAN","GUBRF",
"HEKTS","ISCTR","ISDMR","KCHOL","KRDMD","LOGO","MGROS","ODAS",
"OTKAR","OYAKC","PETKM","PGSUS","SAHOL","SASA","SISE","SKBNK","SMRTG","SOKM",
"TAVHL","TCELL","THYAO","TKFEN","TOASO","TSKB","TTKOM","TTRAK","TUPRS","ULKER",
"VAKBN","VESBE","VESTL","YKBNK"

]


def get_price(symbol):

    try:

        ticker = symbol + ".IS"

        df = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False
        )

        if df is None or len(df) < 50:
            return None

        return df

    except:

        return None


def analyze(symbol):

    df = get_price(symbol)

    if df is None:
        return None

    try:

        df["EMA20"] = df["Close"].ewm(span=20).mean()
        df["EMA50"] = df["Close"].ewm(span=50).mean()

        ema20 = df["EMA20"].iloc[-1]
        ema50 = df["EMA50"].iloc[-1]

        volume = df["Volume"].iloc[-1]
        volume_avg = df["Volume"].rolling(20).mean().iloc[-1]

        score = 0

        if ema20 > ema50:
            score += 50

        if volume > volume_avg:
            score += 50

        return score

    except:

        return None


def scan_bist100():

    results = []

    for stock in BIST100:

        score = analyze(stock)

        if score is None:
            continue

        results.append((stock, score))

        time.sleep(0.2)

    if len(results) == 0:
        return []

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:10]
