import pandas as pd
import requests
import time

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

log_file = "trades_log.csv"

active_symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

print("AI TRADER V25 AUTONOMOUS CALISIYOR...")
send("🧠 V25 FULL AUTO AKTİF")

while True:
    try:
        df = pd.read_csv(log_file)

        if len(df) < 5:
            time.sleep(120)
            continue

        grouped = df.groupby("symbol")["profit"].sum()

        best = grouped.idxmax()
        worst = grouped.idxmin()

        # 💣 otomatik değişim
        if worst in active_symbols:
            active_symbols.remove(worst)
            send(f"⛔ {worst} sistemden çıkarıldı")

        if best not in active_symbols:
            active_symbols.append(best)
            send(f"🚀 {best} sisteme eklendi")

        send(f"📊 AKTİF HİSSELER: {active_symbols}")

    except Exception as e:
        print("HATA:", e)

    time.sleep(180)
