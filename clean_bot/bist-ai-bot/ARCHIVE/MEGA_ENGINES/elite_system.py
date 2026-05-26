import requests
import yfinance as yf
import time

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

last_update_id = None
last_text = None   # 🔥 tekrar engelle

print("🚀 PRO BOT CALISIYOR...")

while True:
    try:
        if last_update_id:
            data = requests.get(url + f"/getUpdates?offset={last_update_id+1}").json()
        else:
            data = requests.get(url + "/getUpdates").json()

        if len(data["result"]) == 0:
            time.sleep(2)
            continue

        # 🔥 SADECE SON MESAJ
        item = data["result"][-1]
        last_update_id = item["update_id"]

        if "message" in item and "text" in item["message"]:
            text = item["message"]["text"]

            # 🔥 AYNI MESAJI TEKRAR İŞLEME
            if text == last_text:
                continue

            last_text = text

            if "/support" in text:
                parts = text.split(" ")

                if len(parts) > 1:
                    symbol = parts[1].upper()

                    df = yf.download(symbol + ".IS", period="10d", interval="1h")

                    df["RSI"] = calculate_rsi(df)
                    df["MA20"] = df["Close"].rolling(20).mean()
                    df["MA50"] = df["Close"].rolling(50).mean()

                    df = df.dropna()

                    if len(df) == 0:
                        continue

                    last = df.iloc[-1]

                    rsi = round(last["RSI"].item(), 2)
                    ma20 = round(last["MA20"].item(), 2)
                    ma50 = round(last["MA50"].item(), 2)
                    price = round(last["Close"].item(), 2)

                    # 🔥 PROFESYONEL STRATEJI
                    if rsi < 30 and price > ma20 and ma20 > ma50:
                        signal = "🚀 AL"
                    elif rsi > 70 and price < ma20:
                        signal = "🔻 SAT"
                    else:
                        signal = "⏳ BEKLE"

                    # 🧠 YORUM
                    if rsi > 70:
                        yorum = "⚠️ Aşırı alım"
                    elif rsi < 30:
                        yorum = "🔥 Aşırı satım"
                    else:
                        yorum = "📊 Nötr"

                    message = f"""📊 {symbol}
Fiyat: {price}
RSI: {rsi}
MA20: {ma20}
MA50: {ma50}

Sinyal: {signal}
Yorum: {yorum}
"""

                else:
                    message = "Kullanım: /support EREGL"

                requests.post(url + "/sendMessage", data={
                    "chat_id": CHAT_ID,
                    "text": message
                })

    except Exception as e:
        print("HATA:", e)

    time.sleep(3)
