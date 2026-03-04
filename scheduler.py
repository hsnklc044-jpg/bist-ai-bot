import schedule
import time

from bot import main


def run_morning():

    print("📡 Sabah radar çalışıyor...")
    main()


def run_midday():

    print("📡 Öğle radar çalışıyor...")
    main()


def run_close():

    print("📡 Kapanış radar çalışıyor...")
    main()


# saatler
schedule.every().day.at("09:30").do(run_morning)
schedule.every().day.at("12:00").do(run_midday)
schedule.every().day.at("17:45").do(run_close)


print("⏱ Scheduler başlatıldı...")


while True:

    schedule.run_pending()

    time.sleep(30)
