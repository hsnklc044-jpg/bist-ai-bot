from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from datetime import datetime

from core.performance_metrics import (
    generate_performance_metrics
)

from core.portfolio_report import (
    generate_portfolio_report
)

from core.alert_engine import (
    generate_alerts
)

from core.market_scan import (
    generate_market_scan
)

from core.rebalancing_engine_v3 import (
    generate_rebalance_report_v3
)


def generate_pdf_report():

    filename = (
        "QuantBIST_Report_"
        + datetime.now().strftime("%Y%m%d")
        + ".pdf"
    )

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "QuantBIST AI Report",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 20)
    )

    sections = [

        (
            "Performance Metrics",
            generate_performance_metrics()
        ),

        (
            "Open Portfolio",
            generate_portfolio_report()
        ),

        (
            "Alert Center",
            generate_alerts()
        ),

        (
            "Market Scan",
            generate_market_scan()
        ),

        (
            "Rebalance Report",
            generate_rebalance_report_v3()
        )

    ]

    for title, content in sections:

        story.append(
            Paragraph(
                title,
                styles["Heading2"]
            )
        )

        story.append(
            Paragraph(
                content.replace(
                    "\n",
                    "<br/>"
                ),
                styles["BodyText"]
            )
        )

        story.append(
            Spacer(1, 15)
        )

    doc.build(story)

    return filename