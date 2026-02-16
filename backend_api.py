from flask import Flask, request, jsonify
import datetime
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# 🔐 Panel şifresi
PANEL_PASSWORD = "44Dupduru--"

# 📊 İzlenen hisseler
HISSELER = [
    "ASELS.IS", "TUPRS.IS", "KCHOL.IS",
    "SISE.IS", "YKBNK.IS", "AKBNK.IS",
    "BIMAS.IS", "THYAO.IS"
]

# --------------------------------------------------
# 🔐 LOGIN
# --------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if data.get("password") == PANEL_PASSWORD:
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 401


# --------------------------------------------------
# 🤖 AI SEÇİLEN HİSSELER
# --------------------------------------------------
@app.route("/signals")
def signals():
    today = datetime.date.today().isoformat()

    return jsonify({
        "date": today,
        "signals": HISSELER
    })


# --------------------------------------------------
# 📈 BACKTEST VERİSİ
# --------------------------------------------------
@app.route("/backtest")
def backtest():
    try:
        data = yf.download(HISSELER, period="6mo")["Adj Close"]

        # Ortalama portföy getirisi
        returns = data.pct_change().mean(axis=1).cumsum()

        return jsonify({
            "dates": returns.index.strftime("%Y-%m-%d").tolist(),
            "values": (returns * 100).round(2).tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# 🚀 ÇALIŞTIR
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
