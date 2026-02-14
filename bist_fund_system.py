import yfinance as yf
import requests

TELEGRAM_TOKEN = "8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ"
CHAT_ID = "1790584407"

bist_list = [
    "AKBNK.IS","GARAN.IS","YKBNK.IS","ISCTR.IS",
    "KCHOL.IS","EREGL.IS","TUPRS.IS","ASELS.IS",
    "SISE.IS","BIMAS.IS","THYAO.IS"
]

def analyze():
    results = []

    for ticker in bist_list:
        try:
            df = yf.download(ticker, period="3mo", progress=False)

            if len(df) < 50:
                continue

            ma20 = df["Close"].rolling(20).mean().iloc[-1]
            ma50 = df["Close"].rolling(50).mean().iloc[-1]
            price = df["Close"].iloc[-1]

            if price > ma20 > ma50:
                change = (price / df["Close"].iloc[-2] - 1) * 100
                results.append(f"{ticker} ↑ %{change:.2f}")

        except:
            pass

    return results


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})


signals = analyze()

if signals:
    msg = "📊 YARIN İÇİN GÜÇLÜ BIST ADAYLARI:\n\n" + "\n".join(signals)
else:
    msg = "Bugün güçlü sinyal yok."

send_telegram(msg)

print("Bitti.")
