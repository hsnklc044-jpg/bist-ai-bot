from flask import Flask, render_template_string
import json
import yfinance as yf
import os

app = Flask(__name__)

AI_FILE = "ai_memory.json"
TRADES_FILE = "open_trades.json"

# ========================
# DOSYA GARANTİ (KRİTİK)
# ========================
def ensure_files():
    if not os.path.exists(AI_FILE):
        with open(AI_FILE, "w") as f:
            json.dump({}, f)

    if not os.path.exists(TRADES_FILE):
        # TEST İÇİN ÖRNEK TRADE KOY (panel boş kalmasın)
        sample = [
            {
                "symbol": "PETKM",
                "price": 21.28,
                "target": 21.96,
                "stop": 21.01,
                "size": 2430
            },
            {
                "symbol": "KRDMD",
                "price": 36.20,
                "target": 39.24,
                "stop": 35.31,
                "size": 752
            }
        ]
        with open(TRADES_FILE, "w") as f:
            json.dump(sample, f)

ensure_files()

# ========================
# HTML
# ========================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI TRADING PANEL</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { background:#0f172a; color:white; font-family:Arial; padding:20px; }
        h1 { color:#38bdf8; }
        .grid { display:flex; flex-wrap:wrap; }
        .card {
            background:#1e293b;
            padding:15px;
            margin:10px;
            border-radius:10px;
            width:260px;
        }
        .green { color:#22c55e; }
        .red { color:#ef4444; }
    </style>
</head>
<body>

<h1>🤖 AI TRADING PANEL</h1>

<h2>📡 Açık İşlemler</h2>
<div class="grid">
{% for t in trades %}
<div class="card">
<b>{{t.symbol}}</b><br>
Fiyat: {{t.price}}<br>
PnL: <span class="{{'green' if t.pnl > 0 else 'red'}}">{{t.pnl}} TL</span><br>
TP mesafe: {{t.tp_dist}}%<br>
SL mesafe: {{t.sl_dist}}%
</div>
{% endfor %}
</div>

<h2>🧠 AI MEMORY</h2>
<div class="grid">
{% for s, d in ai.items() %}
<div class="card">
<b>{{s}}</b><br>
Win: {{d.win}}<br>
Loss: {{d.loss}}
</div>
{% endfor %}
</div>

</body>
</html>
"""

# ========================
# LOAD
# ========================
def load_ai():
    try:
        with open(AI_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def load_trades():
    try:
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# ========================
# CANLI FİYAT
# ========================
def get_price(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1d", interval="5m", progress=False)
        return float(df["Close"].iloc[-1])
    except:
        return None

# ========================
# ROUTE
# ========================
@app.route("/")
def home():

    ai = load_ai()
    trades_raw = load_trades()

    trades = []

    for t in trades_raw:

        price = get_price(t["symbol"])

        if price is None:
            price = t["price"]  # fallback

        pnl = (price - t["price"]) * t["size"]

        tp_dist = ((t["target"] - price) / price) * 100
        sl_dist = ((price - t["stop"]) / price) * 100

        trades.append({
            "symbol": t["symbol"],
            "price": round(price, 2),
            "pnl": int(pnl),
            "tp_dist": round(tp_dist, 2),
            "sl_dist": round(sl_dist, 2)
        })

    return render_template_string(HTML, ai=ai, trades=trades)

# ========================
# RUN
# ========================
if __name__ == "__main__":
    app.run(debug=True)