import schedule
import time

from engine.ultimate_scanner import run_ultimate_scanner


print("🚀 Radar scheduler başlatıldı")


def job():

    try:

        print("📡 BIST AI radar çalışıyor...")

        run_ultimate_scanner()

        print("✅ Tarama tamamlandı")

    except Exception as e:

        print("❌ Scanner hata verdi:", e)



# İlk deploy olduğunda hemen çalıştır
job()


# Sonra her 30 dakikada bir çalıştır
schedule.every(30).minutes.do(job)



while True:

    schedule.run_pending()

    time.sleep(10)
