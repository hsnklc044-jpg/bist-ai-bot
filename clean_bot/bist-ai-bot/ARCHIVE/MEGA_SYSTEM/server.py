from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ==============================
# LOG FILE
# ==============================
def log_trade(data):
    with open("orders.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {data}\n")

# ==============================
# 🔥 BROKER EXECUTION (SIMULATION)
# ==============================
def send_to_broker(order):
    print("📡 EMİR HAZIR:", order)

    # ⚠️ BURAYA GERÇEK API GELECEK
    # örnek:
    # requests.post("broker_api_url", json=order)

# ==============================
# WEBHOOK ENDPOINT
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if not data:
            print("❌ BOŞ DATA GELDİ")
            return jsonify({"status": "error", "msg": "no data"}), 400

        print("\n🔥 WEBHOOK GELDİ:")
        print(data)

        # log
        log_trade(data)

        # order oluştur
        order = {
            "symbol": data.get("symbol"),
            "entry": data.get("entry"),
            "stop": data.get("stop"),
            "target": data.get("target"),
            "time": data.get("time")
        }

        print("🧾 ORDER:", order)

        # broker gönder
        send_to_broker(order)

        return jsonify({"status": "ok"})

    except Exception as e:
        print("❌ SERVER HATA:", e)
        return jsonify({"status": "error"}), 500

# ==============================
# TEST ENDPOINT
# ==============================
@app.route("/", methods=["GET"])
def home():
    return "🚀 Server çalışıyor"

# ==============================
# HEALTH CHECK
# ==============================
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "alive"})

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    print("🚀 SERVER BAŞLATILIYOR...")
    app.run(host="0.0.0.0", port=5000)