import requests
import yfinance as yf
import time

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

symbols = ["EREGL","THYAO","ASELS","BIMAS","YKBNK","AKBNK","KRDMD","SISE","PETKM","TUPRS"]

active_trades = {}

def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

last_update_id = None

print("🚀 FULL BOT CALISIYOR...")

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

            # =========================
            # SUPPORT
            # =========================
            if text.startswith("/support"):

                parts = text.split(" ")

                if len(parts) > 1:
                    symbol = parts[1].upper()

                    df = yf.download(symbol + ".IS", period="5d", interval="1h", progress=False)

                    if df.empty:
                        message = "Veri bulunamadı"
                    else:
                        support = round(df["Low"].min().item(), 2)
                        message = f"📊 {symbol}\nDestek: {support}"

                else:
                    message = "Kullanım: /support EREGL"

                requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": message})


            # =========================
            # RADAR ULTRA PRO++
            # =========================
            if text == "/radar":

                candidates = []

                for symbol in symbols:
                    try:
                        df = yf.download(symbol + ".IS", period="15d", interval="1h", progress=False)

                        if df.empty or len(df) < 60:
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

                        # TREND
                        if price > ma20 > ma50:
                            score += 3

                        # MOMENTUM
                        if 35 < rsi < 55:
                            score += 2

                        # DIP YAKINLIK
                        if abs(price - ma20) / price < 0.015:
                            score += 1

                        # AŞIRI ALIM ELEME
                        if rsi > 70:
                            continue

                        if score >= 4:
                            candidates.append((symbol, score, price, rsi))

                    except:
                        continue

                candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:2]

                if len(candidates) > 0:
                    lines = []

                    for c in candidates:
                        symbol, score, price, rsi = c

                        tp = round(price * 1.025, 2)
                        sl = round(price * 0.98, 2)

                        if symbol in active_trades:
                            continue

                        active_trades[symbol] = {
                            "entry": price,
                            "tp": tp,
                            "sl": sl
                        }

                        lines.append(
                            f"{symbol} ⭐{score}/6\n"
                            f"Fiyat: {round(price,2)}\n"
                            f"RSI: {round(rsi,2)}\n"
                            f"TP: {tp} | SL: {sl}"
                        )

                    if len(lines) > 0:
                        message = "🚀 ULTRA PRO FIRSATLAR:\n\n" + "\n\n".join(lines)
                    else:
                        message = "⚖️ Yeni fırsat yok"

                else:
                    message = "⚖️ Güçlü fırsat yok"

                requests.post(url + "/sendMessage", data={
                    "chat_id": CHAT_ID,
                    "text": message
                })

    except Exception as e:
        print("HATA:", e)

    time.sleep(3)
