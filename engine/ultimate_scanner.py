import yfinance as yf

from engine.ai_scoring_engine import score_stock
from engine.ai_trade_score import calculate_trade_score
from engine.market_mode_ai import get_market_mode
from engine.multi_timeframe_ai import multi_timeframe_trend
from engine.institutional_money_detector import detect_institutional_activity
from engine.relative_strength_engine import relative_strength_vs_index
from engine.trend_engine import detect_trend
from engine.risk_engine import calculate_trade_levels
from engine.elite_signal_filter import filter_elite_signals
from engine.volume_anomaly_engine import detect_volume_anomaly
from engine.signal_memory import is_new_signal
from engine.pro_trading_signal_formatter import format_signal

from app.bist100 import BIST100


LOOKBACK_PERIOD = "3mo"


def download_data(symbol):

    try:

        df = yf.download(
            symbol,
            period=LOOKBACK_PERIOD,
            interval="1d",
            progress=False
        )

        if df is None or df.empty:
            return None

        df.dropna(inplace=True)

        return df

    except Exception as e:

        print("Veri indirilemedi:", symbol, e)
        return None


def volume_spike(df):

    avg_volume = df["Volume"].rolling(20).mean()

    if df["Volume"].iloc[-1] > avg_volume.iloc[-1] * 1.7:
        return True

    return False


def volatility_squeeze(df):

    rolling_std = df["Close"].rolling(20).std()

    current_vol = rolling_std.iloc[-1]
    avg_vol = rolling_std.mean()

    if current_vol < avg_vol * 0.8:
        return True

    return False


def run_ultimate_scan():

    print("🚀 ULTIMATE BIST AI RADAR BAŞLADI")

    results = []

    # Market Mode belirleme
    try:

        market_mode = get_market_mode()
        print("📊 Market Mode:", market_mode)

    except Exception as e:

        print("Market mode okunamadı:", e)
        market_mode = "SIDEWAYS"

    for symbol in BIST100:

        ticker = f"{symbol}.IS"

        df = download_data(ticker)

        if df is None:
            continue

        if len(df) < 80:
            continue

        try:

            score = score_stock(df)

            trade_score = calculate_trade_score(df)

            vol_spike = volume_spike(df)

            squeeze = volatility_squeeze(df)

            anomaly = detect_volume_anomaly(df)
            anomaly_flag = anomaly["volume_anomaly"]

            institutional = detect_institutional_activity(df)
            inst_flag = institutional["institutional_activity"]

            rs_data = relative_strength_vs_index(df)
            rs_flag = rs_data["stronger_than_index"]

            trend_data = detect_trend(df)
            trend_flag = trend_data["trend"]

            # Multi Timeframe trend
            mtf = multi_timeframe_trend(symbol)
            mtf_flag = mtf["strong_trend"]

            trade = calculate_trade_levels(df)

            if trade is None:
                continue

            # Market mode stratejisi
            if market_mode == "BULL":

                condition = trend_flag or trade_score >= 70

            elif market_mode == "SIDEWAYS":

                condition = vol_spike or anomaly_flag or squeeze

            else:  # BEAR

                condition = rs_flag or inst_flag

            # Multi timeframe filtresi
            if condition and mtf_flag:

                # Signal memory (spam önleme)
                if not is_new_signal(symbol):
                    continue

                results.append({
                    "symbol": symbol,
                    "score": score,
                    "ai_score": trade_score,
                    "price": float(df["Close"].iloc[-1]),
                    "volume_spike": vol_spike,
                    "squeeze": squeeze,
                    "volume_anomaly": anomaly_flag,
                    "institutional": inst_flag,
                    "relative_strength": rs_flag,
                    "trend": trend_flag,
                    "mtf_trend": mtf_flag,
                    "entry": trade["entry"],
                    "stop": trade["stop"],
                    "target": trade["target"],
                    "rr": trade["risk_reward"]
                })

        except Exception as e:

            print("Hata:", symbol, e)

    # AI skoruna göre sıralama
    results = sorted(results, key=lambda x: x["ai_score"], reverse=True)

    # Elite filter
    results = filter_elite_signals(results)

    print("✅ Ultimate Radar tamamlandı")

    formatted_signals = []

    for r in results:

        formatted_signals.append(format_signal(r))

    return formatted_signals
