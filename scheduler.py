import schedule
import time

from engine.ultimate_scanner import run_ultimate_scanner


def radar():

    print("📡 BIST radar çalışıyor...")

    results = run_ultimate_scanner()

    if results:

        print("Sinyaller bulundu")

    else:

        print("Radar sinyal bulamadı")


# BIST için en doğru saatler

schedule.every().day.at("10:15").do(radar)
schedule.every().day.at("12:30").do(radar)
schedule.every().day.at("15:30").do(radar)
schedule.every().day.at("17:45").do(radar)


while True:

    schedule.run_pending()

    time.sleep(30)
