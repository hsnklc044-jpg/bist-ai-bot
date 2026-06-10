from flask import Flask

from core.portfolio_report import (
    generate_portfolio_report
)

from core.performance_report import (
    generate_performance_report
)

from core.trade_journal import (
    generate_trade_journal
)

from core.backtest_engine import (
    run_backtest
)

app = Flask(__name__)


@app.route("/")
def home():

    portfolio = generate_portfolio_report()
    performance = generate_performance_report()
    journal = generate_trade_journal()
    backtest = run_backtest("EREGL.IS")

    html = f"""
    <html>

    <head>

        <title>QuantBIST AI Dashboard</title>

        <style>

            body {{

                font-family: Arial;
                margin: 40px;
                background: #f4f4f4;
            }}

            .card {{

                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px #ccc;
            }}

            h1 {{
                color: #222;
            }}

            pre {{

                white-space: pre-wrap;
                font-size: 14px;
            }}

        </style>

    </head>

    <body>

        <h1>🚀 QuantBIST AI Dashboard</h1>

        <div class="card">
            <h2>📂 Portfolio</h2>
            <pre>{portfolio}</pre>
        </div>

        <div class="card">
            <h2>📈 Performance</h2>
            <pre>{performance}</pre>
        </div>

        <div class="card">
            <h2>📒 Trade Journal</h2>
            <pre>{journal}</pre>
        </div>

        <div class="card">
            <h2>📊 Backtest</h2>
            <pre>{backtest}</pre>
        </div>

    </body>

    </html>
    """

    return html


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )