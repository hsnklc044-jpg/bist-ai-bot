from dashboard_metrics import calculate_metrics
from dashboard_report import generate_dashboard


def run_dashboard(trades):

    metrics = calculate_metrics(trades)

    report = generate_dashboard(metrics)

    return report
