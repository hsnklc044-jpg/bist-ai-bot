import time
import schedule
from app.scanner import run_scan

def job():
    print("BIST AI scan running...")
    run_scan()

schedule.every(15).minutes.do(job)

print("AI BIST Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(1)
