import os
import random
import statistics
import psycopg2
import matplotlib
matplotlib.use("Agg")  # Railway için headless backend
import matplotlib.pyplot as plt
from io import BytesIO


# =====================================================
# DATABASE
# =====================================================

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set.")
    return psycopg2.connect(DATABASE_URL)


def fetch_profits():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT profit FROM trades ORDER BY created_at ASC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [float(r[0]) for r in rows if r[0] is not None]
    except Exception as e:
        print(f"Database error: {e}")
        return []


# =====================================================
# EQUITY CURVE
# =====================================================

def calculate_equity_curve(initial_equity=100000):
    profits = fetch_profits()
    equity = initial_equity
    curve = [equity]

    for p in profits:
        equity += p
        curve.append(round(equity, 2))

    return curve


def calculate_drawdown(initial_equity=100000):
    curve = calculate_equity_curve(initial_equity)

    if not curve:
        return 0, 0

    peak = curve[0]
    max_drawdown = 0

    for value in curve:
        if value > peak:
            peak = value

        drawdown = peak - value
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    drawdown_percent = round((max_drawdown / peak) * 100, 2) if peak != 0 else 0
    return round(max_drawdown, 2), drawdown_percent


# =====================================================
# EQUITY CHART (PNG)
# =====================================================

def generate_equity_chart(initial_equity=100000):
    curve = calculate_equity_curve(initial_equity)

    if len(curve) <= 1:
        return None  # Veri yok

    plt.figure(figsize=(8, 4))
    plt.plot(curve, linewidth=2)
    plt.title("Equity Curve")
    plt.xlabel("Trade #")
    plt.ylabel("Equity (TL)")
    plt.grid(True)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    return buffer


# =====================================================
# MONTE CARLO
# =====================================================

def run_monte_carlo(initial_equity=100000, simulations=1000):
    profits = fetch_profits()

    if not profits:
        return {
            "mean_equity": initial_equity,
            "best_case": initial_equity,
            "worst_case": initial_equity,
            "ruin_probability": 0,
        }

    trades = len(profits)
    results = []

    for _ in range(simulations):
        equity = initial_equity
        for _ in range(trades):
            equity += random.choice(profits)
        results.append(equity)

    mean_equity = round(statistics.mean(results), 2)
    best_case = round(max(results), 2)
    worst_case = round(min(results), 2)

    ruin_threshold = initial_equity * 0.5
    ruin_count = sum(1 for r in results if r <= ruin_threshold)
    ruin_probability = round((ruin_count / simulations) * 100, 2)

    return {
        "mean_equity": mean_equity,
        "best_case": best_case,
        "worst_case": worst_case,
        "ruin_probability": ruin_probability,
    }
