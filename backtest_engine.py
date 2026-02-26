import numpy as np
import random
import json
import os
import matplotlib.pyplot as plt

RISK_PER_TRADE = 0.01
START_BALANCE = 100000

TRADE_FILE = "rr_distribution.json"


def generate_mock_distribution():
    """
    Eğer gerçek RR dağılımı yoksa
    örnek institutional dağılım üretir.
    """

    rr_list = []

    for _ in range(200):
        rr = random.uniform(1.8, 3.5)
        rr_list.append(rr)

    with open(TRADE_FILE, "w") as f:
        json.dump(rr_list, f)

    return rr_list


def load_trade_distribution():

    if not os.path.exists(TRADE_FILE):
        return generate_mock_distribution()

    with open(TRADE_FILE, "r") as f:
        return json.load(f)


def run_monte_carlo(simulations=300):

    trades = load_trade_distribution()

    final_balances = []
    max_dd_list = []

    for _ in range(simulations):

        shuffled = trades.copy()
        random.shuffle(shuffled)

        balance = START_BALANCE
        equity = [balance]

        for rr in shuffled:
            risk_amount = balance * RISK_PER_TRADE
            pnl = risk_amount * rr
            balance += pnl
            equity.append(balance)

        equity = np.array(equity)
        peak = np.maximum.accumulate(equity)
        drawdown = (peak - equity) / peak
        max_dd = np.max(drawdown)

        final_balances.append(balance)
        max_dd_list.append(max_dd)

    worst_dd = np.percentile(max_dd_list, 95) * 100
    avg_dd = np.mean(max_dd_list) * 100
    avg_final = np.mean(final_balances)

    plt.figure(figsize=(6,4))
    plt.hist(max_dd_list, bins=25)
    plt.title("Monte Carlo Max DD")
    plt.savefig("montecarlo_dd.png")
    plt.close()

    result = {
        "Simulations": simulations,
        "Avg Final Balance": round(avg_final,2),
        "Average Max DD %": round(avg_dd,2),
        "Worst 5% DD %": round(worst_dd,2)
    }

    return result, None
