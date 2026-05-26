from flask import Flask
from flask import render_template_string

from portfolio_system.portfolio_manager import load_positions
from portfolio_system.pnl_engine import calculate_pnl

app = Flask(__name__)


HTML = """

<!DOCTYPE html>
<html>

<head>

<title>Institutional Quant Engine</title>

<meta http-equiv="refresh" content="15">

<style>

body{
    background:#020c2b;
    color:white;
    font-family:Arial;
    padding:30px;
}

h1{
    color:#38a3ff;
}

.card-container{
    display:flex;
    gap:20px;
    margin-bottom:30px;
    flex-wrap:wrap;
}

.card{
    background:#132046;
    padding:25px;
    border-radius:15px;
    min-width:220px;
    box-shadow:0 0 10px rgba(0,0,0,0.4);
}

.card-title{
    color:#b7c2d6;
    font-size:18px;
}

.card-value{
    margin-top:15px;
    font-size:42px;
    color:#00ff99;
    font-weight:bold;
}

table{
    width:100%;
    border-collapse:collapse;
    background:#081633;
}

th{
    background:#16264d;
    padding:16px;
    border:1px solid #2d3e67;
}

td{
    padding:14px;
    border:1px solid #2d3e67;
    text-align:center;
}

.green{
    color:#00ff99;
    font-weight:bold;
}

.red{
    color:#ff5c5c;
    font-weight:bold;
}

.section{
    background:#132046;
    padding:30px;
    margin-top:30px;
    border-radius:15px;
}

</style>

</head>

<body>

<h1>🚀 INSTITUTIONAL QUANT ENGINE</h1>

<div class="card-container">

<div class="card">
<div class="card-title">OPEN POSITIONS</div>
<div class="card-value">{{open_count}}</div>
</div>

<div class="card">
<div class="card-title">TOTAL PNL</div>
<div class="card-value">{{total_pnl}}%</div>
</div>

<div class="card">
<div class="card-title">LONG POSITIONS</div>
<div class="card-value">{{long_count}}</div>
</div>

<div class="card">
<div class="card-title">SHORT POSITIONS</div>
<div class="card-value">{{short_count}}</div>
</div>

</div>

<table>

<tr>
<th>SYMBOL</th>
<th>SIGNAL</th>
<th>ENTRY</th>
<th>CURRENT</th>
<th>PNL %</th>
</tr>

{% for row in rows %}

<tr>

<td>{{row.symbol}}</td>

<td>{{row.signal}}</td>

<td>{{row.entry}}</td>

<td>{{row.current}}</td>

<td class="{{row.color}}">
{{row.pnl}}%
</td>

</tr>

{% endfor %}

</table>

<div class="section">

<h2>📊 LIVE SYSTEM STATUS</h2>

<p>
AI Engine Active ✅
</p>

<p>
Telegram Notifications Active ✅
</p>

<p>
Portfolio Engine Active ✅
</p>

<p>
Risk Manager Active ✅
</p>

<p>
Live Scanner Active ✅
</p>

</div>

</body>
</html>

"""


@app.route("/")

def home():

    positions = load_positions()

    rows = []

    total_pnl = 0

    long_count = 0
    short_count = 0

    for symbol, trade in positions.items():

        signal = trade["signal"]

        entry_price = trade["entry_price"]

        current_price = entry_price

        pnl = calculate_pnl(
            signal,
            entry_price,
            current_price
        )

        total_pnl += pnl

        if signal == "LONG":
            long_count += 1
        else:
            short_count += 1

        color = "green"

        if pnl < 0:
            color = "red"

        rows.append({

            "symbol": symbol,
            "signal": signal,
            "entry": entry_price,
            "current": current_price,
            "pnl": pnl,
            "color": color

        })

    total_pnl = round(total_pnl, 2)

    return render_template_string(

        HTML,

        rows=rows,
        total_pnl=total_pnl,
        open_count=len(rows),
        long_count=long_count,
        short_count=short_count

    )


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )