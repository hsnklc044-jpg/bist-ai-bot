import pandas as pd


def get_portfolio_table():

    try:

        df = pd.read_csv(
            "data/portfolio_model.csv"
        )

        html = """

        <table
        style="
        width:100%;
        border-collapse:collapse;
        ">

        <tr
        style="
        background:#222;
        color:#00ff88;
        ">

        <th>Symbol</th>
        <th>Price</th>
        <th>Weight</th>
        <th>Lot</th>
        <th>Value</th>

        </tr>

        """

        for _, row in df.iterrows():

            html += f"""

            <tr>

            <td>{row['symbol']}</td>

            <td>{row['price']}</td>

            <td>{row['weight']}%</td>

            <td>{int(row['lot'])}</td>

            <td>{row['value']:,.0f} TL</td>

            </tr>

            """

        html += "</table>"

        return html

    except Exception as e:

        return f"<b>ERROR:</b> {e}"


def get_health_table():

    try:

        rows = [

            ["EREGL", "BUY", 81, "BULLISH"],
            ["ASELS", "WATCH", 55, "SIDEWAYS"],
            ["BIMAS", "BUY", 74, "BULLISH"],
            ["SISE", "SELL", 30, "BEARISH"],
            ["AKBNK", "SELL", 25, "BEARISH"],
            ["TUPRS", "SELL", 30, "BEARISH"]

        ]

        html = """

        <table
        style="
        width:100%;
        border-collapse:collapse;
        ">

        <tr
        style="
        background:#222;
        color:#00ff88;
        ">

        <th>Symbol</th>
        <th>Signal</th>
        <th>Score</th>
        <th>Trend</th>

        </tr>

        """

        for symbol, signal, score, trend in rows:

            color = "#cccccc"

            if signal == "BUY":
                color = "#00ff88"

            elif signal == "SELL":
                color = "#ff4444"

            elif signal == "WATCH":
                color = "#ffaa00"

            html += f"""

            <tr>

            <td>{symbol}</td>

            <td
            style="
            color:{color};
            font-weight:bold;
            ">
            {signal}
            </td>

            <td>{score}</td>

            <td>{trend}</td>

            </tr>

            """

        html += "</table>"

        return html

    except Exception as e:

        return f"<b>ERROR:</b> {e}"