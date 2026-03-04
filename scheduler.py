import time
import schedule
from scanner import run_scan

def job():
    print("BIST scan running...")
    run_scan()

# her 15 dakikada bir çalıştır
schedule.every(15).minutes.do(job)

print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(1)
