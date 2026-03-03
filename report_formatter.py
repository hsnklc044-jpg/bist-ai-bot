# report_formatter.py

def format_report(results):

    if not results:
        return "Bugün uygun sinyal bulunamadı."

    message = "📊 SABAH RAPORU\n\n"

    for symbol, score, category in results:
        message += f"{category}\n"
        message += f"{symbol} – Skor: {round(score,1)}\n\n"

    return message
