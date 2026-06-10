from flask import Flask

from core.equity_chart import (
    generate_equity_chart
)

from core.portfolio_pie_chart import (
    generate_portfolio_pie_chart
)

from core.dashboard_data import (
    get_dashboard_stats
)

from core.dashboard_tables import (
    get_portfolio_table,
    get_health_table
)

from core.dashboard_cards import (
    get_top_signals_card,
    get_summary_card,
    get_rebalance_cards
)

app = Flask(__name__)


@app.route("/")
def home():

    try:
        generate_equity_chart()
    except Exception as e:
        print(e)

    try:
        generate_portfolio_pie_chart()
    except Exception as e:
        print(e)

    stats = get_dashboard_stats()

    portfolio_table = (
        get_portfolio_table()
    )

    health_table = (
        get_health_table()
    )

    top_signals_card = (
        get_top_signals_card()
    )

    summary_card = (
        get_summary_card(
            stats
        )
    )

    rebalance_cards = (
        get_rebalance_cards()
    )

    return f"""

<html>

<head>

<title>QuantBIST AI Dashboard</title>

<style>

body {{

    background:#111;
    color:white;
    font-family:Arial;
    margin:0;
}}

.container {{

    max-width:1600px;
    margin:auto;
    padding:25px;
}}

h1 {{

    color:#00ff88;
    font-size:40px;
    margin-bottom:25px;
}}

h2 {{

    font-size:24px;
    margin-bottom:15px;
}}

.stats {{

    display:flex;
    gap:20px;
    flex-wrap:wrap;
    margin-bottom:25px;
}}

.stat-card {{

    background:#1e1e1e;
    padding:20px;
    border-radius:15px;
    min-width:220px;
    text-align:center;

    box-shadow:
    0 0 12px rgba(0,255,136,0.15);
}}

.stat-title {{

    color:#999;
    font-size:14px;
}}

.stat-value {{

    color:#00ff88;
    font-size:32px;
    font-weight:bold;
    margin-top:10px;
}}

.card {{

    background:#1e1e1e;
    padding:20px;
    border-radius:15px;
    margin-bottom:25px;

    box-shadow:
    0 0 12px rgba(0,255,136,0.15);
}}

.chart-container {{

    text-align:center;
}}

.chart-container img {{

    width:1000px;
    max-width:100%;
    border-radius:10px;
}}

table {{

    width:100%;
    border-collapse:collapse;
    margin-top:10px;
}}

th {{

    background:#222;
    color:#00ff88;
    padding:12px;
    text-align:left;
}}

td {{

    padding:12px;
    border-bottom:1px solid #333;
}}

tr:hover {{

    background:#1a1a1a;
}}

.grid-two {{

    display:grid;
    grid-template-columns:1fr 1fr;
    gap:25px;
}}

</style>

</head>

<body>

<div class="container">

<h1>🚀 QuantBIST AI Dashboard</h1>

<div class="stats">

<div class="stat-card">
<div class="stat-title">
PORTFOLIO VALUE
</div>
<div class="stat-value">
{stats["portfolio"]:,.0f}
</div>
</div>

<div class="stat-card">
<div class="stat-title">
POSITIONS
</div>
<div class="stat-value">
{stats["positions"]}
</div>
</div>

<div class="stat-card">
<div class="stat-title">
CASH
</div>
<div class="stat-value">
{stats["cash"]}
</div>
</div>

<div class="stat-card">
<div class="stat-title">
TOP STOCK
</div>
<div class="stat-value">
{stats["top_stock"].replace(".IS","")}
</div>
</div>

</div>

{top_signals_card}

{summary_card}

<div class="card">

<h2>📈 Portfolio Health</h2>

{health_table}

</div>

<div class="card">

<h2>📈 Equity Curve</h2>

<div class="chart-container">

<img src="/static/equity_curve.png">

</div>

</div>

<div class="card">

<h2>🥧 Portfolio Allocation</h2>

<div class="chart-container">

<img src="/static/portfolio_pie.png">

</div>

</div>

<div class="card">

<h2>💼 Live Portfolio</h2>

{portfolio_table}

</div>

{rebalance_cards}

</div>

</body>

</html>

"""



if __name__ == "__main__":

    print(
        "\n🚀 QuantBIST Dashboard Starting...\n"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )