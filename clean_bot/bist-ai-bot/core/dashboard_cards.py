def get_top_signals_card():

    return """

    <div class='card'>

    <h2>🔥 Top Signals</h2>

    <table>

    <tr>
    <th>Rank</th>
    <th>Symbol</th>
    <th>Score</th>
    </tr>

    <tr>
    <td>1</td>
    <td>HEKTS</td>
    <td>75</td>
    </tr>

    <tr>
    <td>2</td>
    <td>EREGL</td>
    <td>75</td>
    </tr>

    <tr>
    <td>3</td>
    <td>BIMAS</td>
    <td>74</td>
    </tr>

    </table>

    </div>

    """


def get_summary_card(stats):

    return f"""

    <div class='card'>

    <h2>📊 Portfolio Summary</h2>

    <table>

    <tr>
    <td>Portfolio Value</td>
    <td>{stats["portfolio"]:,.0f} TL</td>
    </tr>

    <tr>
    <td>Positions</td>
    <td>{stats["positions"]}</td>
    </tr>

    <tr>
    <td>Cash</td>
    <td>{stats["cash"]} TL</td>
    </tr>

    <tr>
    <td>Top Stock</td>
    <td>{stats["top_stock"]}</td>
    </tr>

    </table>

    </div>

    """


def get_rebalance_cards():

    return """

    <div class='card'>

    <h2>🔄 Rebalance Actions</h2>

    <div style="display:flex;gap:20px;flex-wrap:wrap;">

        <div style="
        background:#3a1111;
        padding:20px;
        border-radius:12px;
        min-width:250px;
        ">

        <h3>🔴 SELL</h3>

        GARAN.IS<br>
        HEKTS.IS<br>
        KCHOL.IS<br>
        PETKM.IS<br>
        SASA.IS<br>
        TCELL.IS<br>
        THYAO.IS<br>
        YKBNK.IS

        </div>

        <div style="
        background:#2e2e12;
        padding:20px;
        border-radius:12px;
        min-width:250px;
        ">

        <h3>🟡 KEEP</h3>

        BIMAS.IS<br>
        EREGL.IS<br>
        SISE.IS<br>
        TUPRS.IS

        </div>

        <div style="
        background:#113a18;
        padding:20px;
        border-radius:12px;
        min-width:250px;
        ">

        <h3>🟢 BUY</h3>

        AKBNK.IS<br>
        ASELS.IS

        </div>

    </div>

    </div>

    """