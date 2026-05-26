# ================= SMART STATE =================
last_risk = None
last_best = None
last_worst = None

def optimize_strategy():
    global weights, last_best, last_worst

    if not os.path.exists(LOG_FILE):
        return

    df = pd.read_csv(LOG_FILE)
    if len(df) < 5:
        return

    perf = df.groupby("strategy")["profit"].sum()

    best = perf.idxmax()
    worst = perf.idxmin()

    weights[best] += 0.2
    weights[worst] -= 0.2

    weights[best] = min(weights[best], 2)
    weights[worst] = max(weights[worst], 0.5)

    # 💣 SADECE DEĞİŞİRSE MESAJ
    if best != last_best or worst != last_worst:
        send(f"⚖️ STRATEGY UPDATE\nBest: {best}\nWorst: {worst}")
        last_best = best
        last_worst = worst

def optimize_risk():
    global risk_pct, last_risk

    if not os.path.exists(LOG_FILE):
        return

    df = pd.read_csv(LOG_FILE)
    if len(df) < 5:
        return

    old_risk = risk_pct

    recent = df.tail(5)["profit"].sum()

    if recent > 0:
        risk_pct += 0.002
    else:
        risk_pct -= 0.002

    risk_pct = max(0.002, min(risk_pct, 0.02))

    # 💣 SADECE DEĞİŞİRSE MESAJ
    if last_risk is None or abs(risk_pct - last_risk) > 0.0001:
        send(f"💰 RISK UPDATE: {round(risk_pct*100,2)}%")
        last_risk = risk_pct
