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

sent_signals = {}  # 🔥 spam engelle

def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

print("🚀 ULTRA PRO RADAR CALISIYOR...")

while True:
    try:
        candidates = []

        for symbol in symbols:
            try:
                df = yf.download(symbol + ".IS", period="15d", interval="1h")

                if len(df) < 60:
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

                score = 0

                # 🔥 TREND
                if price > ma20 > ma50:
                    score += 2

                # 🔥 RSI
                if 30 < rsi < 45:
                    score += 2
                elif 45 <= rsi < 55:
                    score += 1

                # 🔥 BREAKOUT YAKINLIK
                if abs(price - ma20) / price < 0.02:
                    score += 1

                if score >= 3:
                    candidates.append({
                        "symbol": symbol,
                        "score": score,
                        "price": price,
                        "rsi": rsi
                    })

            except:
                continue

        # 🔥 EN İYİ 3
        candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:3]

        new_signals = []

        for c in candidates:
            symbol = c["symbol"]
            score = c["score"]

            # 🔥 aynı sinyal tekrar gönderme
            if symbol in sent_signals and sent_signals[symbol] == score:
                continue

            sent_signals[symbol] = score

            price = round(c["price"], 2)
            rsi = round(c["rsi"], 2)

            # 🎯 TP / SL
            tp = round(price * 1.03, 2)
            sl = round(price * 0.97, 2)

            new_signals.append(
                f"{symbol} ⭐{score}/6\n"
                f"Fiyat: {price}\n"
                f"RSI: {rsi}\n"
                f"TP: {tp} | SL: {sl}\n"
            )

        if len(new_signals) > 0:
            message = "🚀 ULTRA PRO FIRSATLAR:\n\n" + "\n".join(new_signals)

            requests.post(url + "/sendMessage", data={
                "chat_id": CHAT_ID,
                "text": message
            })

    except Exception as e:
        print("HATA:", e)

    time.sleep(300)
