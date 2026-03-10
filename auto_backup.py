import os
import time
from datetime import datetime

print("BIST AI Auto Backup System Started")

while True:
    try:
        print("Backup running:", datetime.now())

        os.system("git add .")
        os.system(f'git commit -m "auto backup {datetime.now()}"')
        os.system("git push origin main")

        print("Backup completed")

    except Exception as e:
        print("Backup error:", e)

    time.sleep(1800)  # 30 dakika