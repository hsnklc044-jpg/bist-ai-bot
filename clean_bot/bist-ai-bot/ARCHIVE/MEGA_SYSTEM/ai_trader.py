import requests
import yfinance as yf
import time

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

symbols = ["EREGL","THYAO","ASELS","BIMAS","YKBNK","AKBNK","KRDMD","SISE","PETKM","TUPRS"]

last_update_id = None
last_sent = ""

def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

print("🔥 STABLE AI CALISIYOR...")

while True:
    try:
        data = requests.get(url + "/getUpdates").json()

        for item in data["result"]:
            uid = item["update_id"]

            if last_update_id is None:
                last_update_id = uid
                continue

            if uid <= last_update_id:
                continue

            last_update_id = uid

            if "message" not in item or "text" not in item["message"]:
                continue

            text = item["message"]["text"]

            if text == "/radar":

                results = []

                for s in symbols:
                    try:
                        df = yf.download(s + ".IS", period="10d", interval="1h", progress=False)

                        if df.empty or len(df) < 30:
                            continue

                        df["RSI"] = calculate_rsi(df)
                        df["MA20"] = df["Close"].rolling(20).mean()
                        df = df.dropna()

                        last = df.iloc[-1]

                        price = float(last["Close"])
                        rsi = float(last["RSI"])
                        ma20 = float(last["MA20"])

                        # 🎯 ELIT filtre
                        if price > ma20 and 40 < rsi < 60:
                            results.append(f"{s} | {round(price,2)} | RSI:{round(rsi,2)}")

                    except:
                        continue

                if results:
                    message = "🎯 ELIT FIRSATLAR:\n\n" + "\n".join(results[:5])
                else:
                    message = "⚖️ Sinyal yok"

                # 🚫 DUPLICATE ENGELLE
                if message != last_sent:
                    requests.post(url + "/sendMessage", data={
                        "chat_id": CHAT_ID,
                        "text": message
                    })
                    last_sent = message

    except Exception as e:
        print("HATA:", e)

    time.sleep(5)
