import time
import yfinance as yf
import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]
SCAN_INTERVAL = 5

position = None

TEST_MODE = True


# --- MARKET ---
def is_market_open():
    if TEST_MODE:
        return True

    now = datetime.datetime.now()
    start = now.replace(hour=9, minute=40, second=0)
    end = now.replace(hour=18, minute=10, second=0)

    return start <= now <= end


# --- DATA ---
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)

        if df is None or df.empty:
            df = yf.download(symbol, period="1d", interval="5m", progress=False)

        return df
    except:
        return None


# --- SCORE ---
def calculate_score(df):
    close = df["Close"]
    volume = df["Volume"]

    if len(close) < 25:
        return 0, 0

    price = close.iloc[-1].item()

    ma5 = close.rolling(5).mean().iloc[-1].item()
    ma10 = close.rolling(10).mean().iloc[-1].item()
    ma20 = close.rolling(20).mean().iloc[-1].item()

    score = 0

    # TREND
    if ma5 > ma10:
        score += 1
    if ma10 > ma20:
        score += 1

    # MOMENTUM
    last2 = close.iloc[-2:].values
    if last2[1] > last2[0]:
        score += 1

    # VOLUME
    vol_now = volume.iloc[-1].item()
    vol_avg = volume.rolling(10).mean().iloc[-1].item()
    if vol_now > vol_avg * 1.2:
        score += 1

    return score, price


# --- EXIT ---
def check_exit(entry_price, entry_time, price):
    pnl = price - entry_price

    # STOP
    if price < entry_price * 0.99:
        return True, "STOP"

    # TAKE PROFIT
    if price > entry_price * 1.008:
        return True, "TP"

    # NO MOVE
    if time.time() - entry_time > 60:
        if abs(price - entry_price) < entry_price * 0.002:
            return True, "NO MOVE"

    return False, None


print("🚀 PRO SMART RANKING SWITCH FINAL STARTED")

while True:

    if not is_market_open():
        print("⏸️ MARKET CLOSED")
        time.sleep(60)
        continue

    best_symbol = None
    best_score = 0
    best_price = 0

    scores = {}

    for symbol in SYMBOLS:

        df = get_data(symbol)

        if df is None or df.empty:
            print(f"❌ DATA YOK {symbol}")
            continue

        score, price = calculate_score(df)
        scores[symbol] = (score, price)

        print(f"📊 {symbol} | score:{score}")

        if score > best_score:
            best_score = score
            best_symbol = symbol
            best_price = price

        time.sleep(0.3)

    print("-" * 30)

    # --- ENTRY ---
    if position is None:

        if best_score >= 3:
            position = {
                "symbol": best_symbol,
                "price": best_price,
                "time": time.time()
            }

            print(f"🟢 BUY {best_symbol} | {best_price:.2f} | score:{best_score}")
        else:
            print("⏸️ NO TRADE")

    # --- HOLD / SWITCH / EXIT ---
    else:

        current_symbol = position["symbol"]
        entry_price = position["price"]
        entry_time = position["time"]

        current_score, current_price = scores.get(current_symbol, (0, entry_price))

        pnl = current_price - entry_price

        # 🔥 SMART SWITCH
        if best_symbol != current_symbol:

            if best_score >= 3 and current_score < best_score:
                print(f"🔄 SWITCH {current_symbol} → {best_symbol}")

                position = {
                    "symbol": best_symbol,
                    "price": best_price,
                    "time": time.time()
                }

            else:
                exit_flag, reason = check_exit(entry_price, entry_time, current_price)

                if exit_flag:
                    print(f"🔴 EXIT {current_symbol} | {reason} | PnL:{pnl:.2f}")
                    position = None
                else:
                    print(f"🟡 HOLD {current_symbol} | {current_price:.2f} | PnL:{pnl:.2f}")

        else:
            exit_flag, reason = check_exit(entry_price, entry_time, current_price)

            if exit_flag:
                print(f"🔴 EXIT {current_symbol} | {reason} | PnL:{pnl:.2f}")
                position = None
            else:
                print(f"🟡 HOLD {current_symbol} | {current_price:.2f} | PnL:{pnl:.2f}")

    print("=" * 40)
    time.sleep(SCAN_INTERVAL)