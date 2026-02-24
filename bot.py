import os
import requests
from flask import Flask
from bist30 import scan_bist30
from account_config import load_config, update_account_size, update_risk_percent
from performance_tracker import check_performance, generate_statistics

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    if not TOKEN or not CHAT_ID:
        print("Environment variables eksik")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram hata:", e)


@app.route("/")
def home():
    return "BIST AI ELİT PRO aktif."


@app.route("/morning_scan")
def morning_scan():

    config = load_config()

    results = scan_bist30(
        config["account_size"],
        config["risk_percent"]
    )

    if not results:
        return "Sinyal bulunamadı."

    for message in results:
        send_message(message)

    return "Tarama tamamlandı."


@app.route("/sermaye/<int:yeni>")
def set_account(yeni):
    update_account_size(yeni)
    send_message(f"💰 Sermaye güncellendi: {yeni} TL")
    return "OK"


@app.route("/risk/<float:yeni>")
def set_risk(yeni):
    update_risk_percent(yeni / 100)
    send_message(f"⚖️ Risk oranı güncellendi: %{yeni}")
    return "OK"


@app.route("/performance_check")
def performance_check():
    history = check_performance()

    report = "📊 PERFORMANS RAPORU\n\n"

    for trade in history:
        report += (
            f"{trade['symbol']} | "
            f"Durum: {trade['status']} | "
            f"Giriş: {trade['entry']}\n"
        )

    send_message(report)

    return "Rapor gönderildi."


@app.route("/stats")
def stats():

    stats_data = generate_statistics()

    message = (
        f"📊 SİSTEM İSTATİSTİKLERİ\n\n"
        f"Toplam İşlem: {stats_data['total']}\n"
        f"Kazanan: {stats_data['wins']}\n"
        f"Kaybeden: {stats_data['losses']}\n"
        f"Win Rate: %{stats_data['win_rate']}\n"
        f"Ortalama R/R: {stats_data['avg_rr']}"
    )

    send_message(message)

    return "İstatistik gönderildi."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
