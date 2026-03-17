from scanner_ai import run_ai_scanner

def job():

    print("AI SCAN BASLADI")

    results = run_ai_scanner()

    if not results:
        print("Sinyal yok")
    else:
        for r in results:
            print(
                f"{r['symbol']} | Score:{r['score']} | Entry:{r['entry']} | Stop:{r['stop']} | Target:{r['target']} | RR:{r['rr']} | {r['confidence']}"
            )

if __name__ == "__main__":
    job()
