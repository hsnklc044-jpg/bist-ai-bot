import pandas as pd
import requests
import time
import os

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

log_file = "trades_log.csv"

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

print("AI TRADER V23 DASHBOARD CALISIYOR...")
send("📊 V23 DASHBOARD AKTİF")

while True:
    try:

        if not os.path.exists(log_file):
            send("⚠️ Veri yok - Dashboard bekliyor")
            time.sleep(60)
            continue

        df = pd.read_csv(log_file)

        if len(df) == 0:
            send("⚠️ Veri boş")
            time.sleep(60)
            continue

        total = len(df)
        wins = len(df[df["result"] == "WIN"])
        losses = len(df[df["result"] == "LOSS"])

        winrate = round((wins / total) * 100, 2) if total > 0 else 0
        total_profit = round(df["profit"].sum(), 2)

        best_symbol = df.groupby("symbol")["profit"].sum().idxmax()
        worst_symbol = df.groupby("symbol")["profit"].sum().idxmin()

        report = f"""
📊 SYSTEM DASHBOARD

Total Trade: {total}
Win: {wins} | Loss: {losses}
Winrate: {winrate}%

Profit: {total_profit}

Best: {best_symbol}
Worst: {worst_symbol}
"""

        send(report)

    except Exception as e:
        print("HATA:", e)

    time.sleep(300)
