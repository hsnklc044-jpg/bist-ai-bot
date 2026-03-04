from app.scanner import run_scanner
from app.telegram_sender import send_telegram_message

from engine.portfolio_engine import build_portfolio, format_portfolio_message


def run_radar():

    print("📡 Radar taraması başlıyor...")

    try:

        # hisseleri tara
        results = run_scanner()

        if not results:
            send_telegram_message("Radar sonuç bulamadı.")
            return

        # portföy oluştur
        portfolio = build_portfolio(results)

        # mesaj formatla
        message = format_portfolio_message(portfolio)

        # telegram gönder
        send_telegram_message(message)

        print("✅ Radar tamamlandı")

    except Exception as e:

        error_msg = f"Radar hata verdi: {str(e)}"

        print(error_msg)

        send_telegram_message(error_msg)
