from core.alert_engine import generate_alerts


def get_alert_card():

    report = generate_alerts()

    html = f"""
    <div class="card">

        <h2>🚨 Alert Center</h2>

        <pre style="
        white-space:pre-wrap;
        color:#ffffff;
        font-size:14px;
        line-height:1.5;
        ">
{report}
        </pre>

    </div>
    """

    return html