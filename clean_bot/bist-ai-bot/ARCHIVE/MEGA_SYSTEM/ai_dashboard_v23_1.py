import pandas as pd
import requests
import time
import os
import random
from datetime import datetime

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

log_file = "trades_log.csv"

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# dosya yoksa oluştur
if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write("time,symbol,entry,tp,sl,result,profit\n")

print("AI TRADER V23.1 FAKE DATA CALISIYOR...")
send("🧠 V23.1 FAKE DATA AKTİF")

while True:
    try:

        df = pd.read_csv(log_file)

        # veri yoksa FAKE üret
        if len(df) < 5:

            symbol = random.choice(["THYAO","YKBNK","AKBNK","BIMAS","EREGL"])
            entry = round(random.uniform(30, 800), 2)

            result = random.choice(["WIN","LOSS"])

            profit = round(random.uniform(100, 500), 2)
            if result == "LOSS":
                profit = -profit

            with open(log_file, "a") as f:
                f.write(f"{datetime.now()},{symbol},{entry},0,0,{result},{profit}\n")

            send("⚡ FAKE DATA EKLENDİ")

        # dashboard
        df = pd.read_csv(log_file)

        total = len(df)
        wins = len(df[df["result"] == "WIN"])
        losses = len(df[df["result"] == "LOSS"])

        winrate = round((wins / total) * 100, 2)
        total_profit = round(df["profit"].sum(), 2)

        best = df.groupby("symbol")["profit"].sum().idxmax()
        worst = df.groupby("symbol")["profit"].sum().idxmin()

        send(f"""
📊 DASHBOARD

Trade: {total}
Win: {wins} Loss: {losses}
Winrate: {winrate}%

Profit: {total_profit}

Best: {best}
Worst: {worst}
""")

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
