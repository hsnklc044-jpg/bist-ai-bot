<<<<<<< HEAD
import numpy as np

from scanner import scan_market
from market_regime import analyze_market
from sector_analyzer import analyze_sectors
from market_heatmap import market_heatmap
from probability_engine import trade_probability


def calculate_trade_levels(entry):

    volatility = entry * 0.02

    target = entry + volatility * 2
    stop = entry - volatility * 1.2

    return round(target,2), round(stop,2)


def calculate_position_size(entry, stop, capital=100000, risk_percent=1):

    risk_amount = capital * (risk_percent/100)

    risk_per_share = entry - stop

    if risk_per_share <= 0:
        return 0

    size = risk_amount / risk_per_share

    return int(size)
=======
from scanner import scan_market
>>>>>>> b473b179fde9679eff721a025c85876a830c31be


def run_radar_cycle():

<<<<<<< HEAD
    print("🔎 Market taranıyor...\n")

    trend, risk, mode = analyze_market()

    print("🧠 MARKET AI")
    print("Market Trend :",trend)
    print("Market Risk  :",risk)
    print("Trade Mode   :",mode)
    print()

    sectors = analyze_sectors()

    print("🏭 SECTOR STRENGTH")

    for s in sectors[:5]:
        print(f"{s['sector']} | {s['score']}%")

    print()

    heatmap = market_heatmap()

    print("🔥 MARKET HEATMAP")

    for h in heatmap[:5]:
        print(f"{h['ticker']} | {h['score']}%")

    print()

    signals, volume_leaders, momentum_leaders, smart_money, ai_trades, intraday_breakouts, early_breakouts = scan_market()

    if signals:

        print("🚨 Sinyaller bulundu:")

        for s in signals:

            ticker = s["ticker"]
            entry = s["entry"]
            rsi = s["rsi"]
            score = s["success"]

            momentum = score / 10
            volume_ratio = 2

            target, stop = calculate_trade_levels(entry)

            size = calculate_position_size(entry, stop)

            probability = trade_probability(rsi, momentum, volume_ratio, score)

            print(
                f"{ticker} | Entry {entry} | Target {target} | Stop {stop} | Size {size} | Prob {probability}%"
            )

    else:

        print("Sinyal bulunamadı")

    print()

    if ai_trades:

        print("🏆 TOP AI TRADES")

        for a in ai_trades:
            print(f"{a['ticker']} | Score {a['score']} | Entry {a['entry']}")

        print()

    if early_breakouts:

        print("⚡ EARLY BREAKOUTS")

        for e in early_breakouts:
            print(f"{e['ticker']} | Score {e['score']}")

        print()

    if volume_leaders:

        print("🔥 Volume Leaders:")

        for v in volume_leaders:
            print(f"{v['ticker']} | Volume x{v['volume_ratio']}")

        print()

    if momentum_leaders:

        print("⚡ Momentum Leaders:")

        for m in momentum_leaders:
            print(f"{m['ticker']} | +{m['momentum']}%")

        print()

    if smart_money:

        print("💰 Smart Money:")

        for sm in smart_money:
            print(f"{sm['ticker']} | +{sm['momentum']}% | Vol x{sm['volume_ratio']}")

        print()

    if intraday_breakouts:

        print("⚡ INTRADAY BREAKOUTS:")

        for b in intraday_breakouts:
            print(f"{b['ticker']} | +{b['momentum']}% | Vol x{b['volume']}")

        print()
=======
    print("📡 Market taranıyor...")

    signals = scan_market()

    if signals:
        print("🚨 Sinyaller:")
        for s in signals:
            print(s["ticker"], s["signal"], s["entry"])
    else:
        print("Sinyal bulunamadı")

    return signals
>>>>>>> b473b179fde9679eff721a025c85876a830c31be
