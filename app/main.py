from app.scanner import scan_market
from app.telegram_sender import send_telegram


def run():

    print("🚀 BIST AI BOT ÇALIŞIYOR...")

    try:
        top3 = scan_market()

        if not top3:
            send_telegram("Bugün uygun sinyal bulunamadı.")
            print("Sinyal bulunamadı.")
            return

        message = "🚀 BIST30 GÜNLÜK TARAMA\n\n"

        for i, stock in enumerate(top3, 1):
            message += (
                f"{i}. {stock['symbol']} | "
                f"RSI: {round(float(stock['rsi']),2)} | "
                f"Skor: {round(float(stock['score']),2)}\n"
            )

        send_telegram(message)

        print("Telegram mesajı gönderildi.")

    except Exception as e:
        print("HATA:", str(e))


if __name__ == "__main__":
    run()
