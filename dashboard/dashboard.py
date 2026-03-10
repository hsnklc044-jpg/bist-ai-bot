from flask import Flask
from supabase_engine import supabase

app = Flask(__name__)


@app.route("/")
def home():

    signals = supabase.table("signals").select("*").limit(20).execute()
    trades = supabase.table("trades").select("*").limit(20).execute()

    html = "<h1>BIST AI Dashboard</h1>"

    html += "<h2>Son Sinyaller</h2>"

    for s in signals.data:

        html += f"""
        <p>
        {s['symbol']} |
        {s['signal']} |
        Score: {s['score']}
        </p>
        """

    html += "<h2>Trade Geçmişi</h2>"

    for t in trades.data:

        html += f"""
        <p>
        {t['symbol']} |
        Entry: {t['entry_price']} |
        Profit: {t['profit']} |
        Status: {t['status']}
        </p>
        """

    return html


app.run(port=5000)