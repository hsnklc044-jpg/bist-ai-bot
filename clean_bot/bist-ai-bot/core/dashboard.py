from flask import Flask, render_template_string
from datetime import datetime
from scanner_feed import ai_data

app = Flask(__name__)

HTML = """

<!DOCTYPE html>
<html>

<head>

<title>Institutional Quant Engine</title>

<style>

body{
    background:#020b4f;
    color:white;
    font-family:Arial;
    padding:20px;
}

.card-container{
    display:flex;
    gap:20px;
    margin-bottom:30px;
}

.card{
    background:#1b2a6b;
    padding:20px;
    border-radius:14px;
    width:220px;
}

.value{
    color:#00ffbf;
    font-size:24px;
    font-weight:bold;
}

.section{
    background:#1b2a6b;
    padding:20px;
    border-radius:18px;
    margin-top:30px;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}

th,td{
    border:1px solid #31408d;
    padding:12px;
    text-align:center;
}

th{
    background:#22357f;
}

.long{
    color:#00ffbf;
    font-weight:bold;
}

.short{
    color:#ff5c7a;
    font-weight:bold;
}

.header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:30px;
}

.live-status{
    color:#00ffbf;
    font-weight:bold;
}

.clock{
    font-size:28px;
    color:white;
}

</style>

</head>

<body>

<div class="header">

<div>

<h1>🚀 INSTITUTIONAL QUANT ENGINE</h1>

<p class="live-status">
LIVE AI MARKET TERMINAL
</p>

</div>

<div style="text-align:right;">

<div id="clock" class="clock"></div>

<p class="live-status">
MARKET STATUS: ONLINE
</p>

</div>

</div>

<div class="card-container">

<div class="card">
OPEN POSITIONS
<div class="value">{{ open_positions }}</div>
</div>

<div class="card">
TOTAL PNL
<div class="value">{{ total_pnl }}%</div>
</div>

<div class="card">
LONG POSITIONS
<div class="value">{{ long_count }}</div>
</div>

<div class="card">
SHORT POSITIONS
<div class="value">{{ short_count }}</div>
</div>

</div>

<div class="section">

<h2>📊 LIVE PORTFOLIO</h2>

<table>

<tr>
<th>SYMBOL</th>
<th>SIGNAL</th>
<th>ENTRY</th>
<th>CURRENT</th>
<th>PNL %</th>
</tr>

{% for p in portfolio %}

<tr>

<td>{{ p.symbol }}</td>

<td class="{{ p.signal.lower() }}">
{{ p.signal }}
</td>

<td>{{ p.entry }}</td>

<td>{{ p.current }}</td>

<td class="long">
{{ p.pnl }}%
</td>

</tr>

{% endfor %}

</table>

</div>

<div class="section">

<h2>🟢 TOP LONG OPPORTUNITIES</h2>

<table>

<tr>
<th>SYMBOL</th>
<th>AI SCORE</th>
<th>TREND</th>
<th>SIGNAL</th>
</tr>

{% for s in longs %}

<tr>

<td>{{ s.symbol }}</td>

<td class="long">
{{ s.score }}
</td>

<td>{{ s.trend }}</td>

<td class="long">
{{ s.signal }}
</td>

</tr>

{% endfor %}

</table>

</div>

<div class="section">

<h2>🔴 TOP SHORT OPPORTUNITIES</h2>

<table>

<tr>
<th>SYMBOL</th>
<th>AI SCORE</th>
<th>TREND</th>
<th>SIGNAL</th>
</tr>

{% for s in shorts %}

<tr>

<td>{{ s.symbol }}</td>

<td class="short">
{{ s.score }}
</td>

<td>{{ s.trend }}</td>

<td class="short">
{{ s.signal }}
</td>

</tr>

{% endfor %}

</table>

</div>

<script>

setTimeout(function(){

    location.reload();

}, 5000);

function updateClock(){

    const now = new Date();

    document.getElementById("clock").innerHTML =
        now.toLocaleTimeString();

}

setInterval(updateClock,1000);

updateClock();

</script>

</body>

</html>

"""

@app.route("/")

def dashboard():

    portfolio = [

        {
            "symbol":"TUPRS.IS",
            "signal":"SHORT",
            "entry":250.5,
            "current":248.2,
            "pnl":0.92
        },

        {
            "symbol":"SISE.IS",
            "signal":"LONG",
            "entry":50.4,
            "current":52.1,
            "pnl":3.37
        },

        {
            "symbol":"ASELS.IS",
            "signal":"LONG",
            "entry":413,
            "current":425,
            "pnl":2.91
        },

        {
            "symbol":"THYAO.IS",
            "signal":"SHORT",
            "entry":305,
            "current":298.7,
            "pnl":2.07
        }
    ]

    longs = []
    shorts = []

    for stock in ai_data:

        if stock["signal"] == "LONG":

            longs.append(stock)

        elif stock["signal"] == "SHORT":

            shorts.append(stock)

    longs = sorted(
        longs,
        key=lambda x:x["score"],
        reverse=True
    )[:10]

    shorts = sorted(
        shorts,
        key=lambda x:x["score"]
    )[:10]

    return render_template_string(

        HTML,

        portfolio=portfolio,

        longs=longs,

        shorts=shorts,

        open_positions=len(portfolio),

        total_pnl=9.27,

        long_count=len(longs),

        short_count=len(shorts),

        now=datetime.now()
    )

if __name__ == "__main__":

    app.run(debug=True)