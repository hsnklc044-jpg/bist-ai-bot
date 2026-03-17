from scanner_ai import run_ai_scanner
from datetime import datetime
import csv
import os

FILE_NAME = "signals_log.csv"

def save_results(results):

    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "time", "symbol", "score", "entry",
                "stop", "target", "rr", "confidence"
            ])

        for r in results:
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                r["symbol"],
                r["score"],
                r["entry"],
                r["stop"],
                r["target"],
                r["rr"],
                r["confidence"]
            ])


if __name__ == "__main__":

    print("BIST AI RADAR BASLADI")

    results = run_ai_scanner()

    if not results:
        print("Sinyal yok")
    else:
        for r in results:
            print(
                f"{r['symbol']} | Score:{r['score']} | Entry:{r['entry']} | "
                f"Stop:{r['stop']} | Target:{r['target']} | RR:{r['rr']} | {r['confidence']}"
            )

        save_results(results)
        print("\nKaydedildi: signals_log.csv")
