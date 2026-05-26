import pandas as pd
import requests
import time

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

log_file = "trades_log.csv"

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

print("AI TRADER V24 OPTIMIZATION CALISIYOR...")
send("🧠 V24 AUTO OPTIMIZATION AKTİF")

while True:
    try:
        df = pd.read_csv(log_file)

        if len(df) < 5:
            send("⚠️ Veri az - optimizasyon bekliyor")
            time.sleep(120)
            continue

        grouped = df.groupby("symbol")["profit"].sum()

        best = grouped.idxmax()
        worst = grouped.idxmin()

        if grouped[worst] < 0:
            send(f"⚠️ Zayıf performans: {worst} azaltılmalı")

        if grouped[best] > 0:
            send(f"🚀 Güçlü performans: {best} artırılmalı")

    except Exception as e:
        print("HATA:", e)

    time.sleep(180)
