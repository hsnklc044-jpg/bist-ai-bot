import os
import requests

from scanner import scan_market
from market_regime import get_market_regime
from sector_rotation import get_strong_sector
from crash_detector import market_risk
from risk_manager import position_size
from portfolio_builder import build_portfolio


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        r = requests.post(url, data=payload)

        print("Telegram response:", r.text)

    except Exception as e:

        print("Telegram gönderim hatası:", e)


def build_message(signals, regime, sector, risk, portfolio):

    message = f"""
🚀 BIST QUANT RADAR

📊 MARKET: {regime}
🏭 STRONG SECTOR: {sector}

⚠️ MARKET RISK: {risk}

🔥 TOP AI SIGNALS
"""

    for s in signals:

        lot = position_size(100000, 1, s['entry'], s['stop'])

        message += f"""
📈 {s['ticker']}

AI Score: {s['score']}
Momentum: {s['momentum']}

Pattern: {s['pattern']}
Trend TF: {s['timeframe']}

Breakout: {s['breakout']}
Smart Money: {s['smart_money']}

Entry: {s['entry']}
Stop: {s['stop']}
Target: {s['target']}

Risk: {s['risk']}%
Reward: {s['reward']}%

Lot Size: {lot}

-----------------------
"""

    message += "\n📊 PORTFOLIO SUGGESTION\n"

    for p in portfolio:

        message += f"{p['ticker']} : %{p['weight']}\n"

    return message


def run_bot():

    print("Bot başlatıldı")
    print("BIST AI Bot çalışıyor...")

    if not TOKEN or not CHAT_ID:

        print("Telegram TOKEN veya CHAT_ID eksik")

        return

    try:

        regime = get_market_regime()

        sector = get_strong_sector()

        risk = market_risk()

        signals = scan_market()

        if not signals:

            print("Sinyal bulunamadı")

            return

        portfolio = build_portfolio(signals)

        message = build_message(signals, regime, sector, risk, portfolio)

        send_telegram(message)

    except Exception as e:

        print("Bot hata verdi:", e)


if __name__ == "__main__":

    run_bot()
