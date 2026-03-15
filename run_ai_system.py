import time
import subprocess

print("🚀 AI Trading System Starting")


while True:

    print("Running market scan")

    subprocess.run(["python","auto_scan_engine.py"])

    subprocess.run(["python","momentum_engine.py"])

    subprocess.run(["python","smart_money_engine.py"])

    subprocess.run(["python","prediction_engine.py"])

    subprocess.run(["python","decision_engine.py"])

    subprocess.run(["python","risk_engine.py"])

    subprocess.run(["python","ultra_signal_engine.py"])

    subprocess.run(["python","telegram_signal_engine.py"])

    subprocess.run(["python","learning_engine.py"])


    print("Cycle complete")

    time.sleep(300)
