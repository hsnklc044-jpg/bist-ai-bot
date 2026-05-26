import requests
import yfinance as yf
import time

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

symbols = [
    "EREGL","THYAO","KRDMD","SISE","ASELS","TUPRS","BIMAS",
    "AKBNK","GARAN","YKBNK","ISCTR","SAHOL","KOZAL","PETKM"
]

def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

print("🚀 RADAR PRO CALISIYOR...")

while True:
    try:
        fırsatlar = []

        for symbol in symbols:
            try:
                df = yf.download(symbol + ".IS", period="10d", interval="1h")

                if len(df) < 50:
                    continue

                df["RSI"] = calculate_rsi(df)
                df["MA20"] = df["Close"].rolling(20).mean()
                df["MA50"] = df["Close"].rolling(50).mean()

                df = df.dropna()
                last = df.iloc[-1]

                price = last["Close"].item()
                rsi = last["RSI"].item()
                ma20 = last["MA20"].item()
                ma50 = last["MA50"].item()

                # 🔥 PRO FİLTRE
                if price > ma20 > ma50 and 30 < rsi < 55:
                    fırsatlar.append(f"{symbol} → RSI:{round(rsi,1)} 🚀")

            except:
                continue

        if len(fırsatlar) > 0:
            mesaj = "🚀 AL FIRSATLARI:\n\n" + "\n".join(fırsatlar)
        else:
            mesaj = "⚖️ Şu an güçlü fırsat yok"

        requests.post(url + "/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": mesaj
        })

    except Exception as e:
        print("HATA:", e)

    time.sleep(300)  # 🔥 5 dakikada bir çalışır
