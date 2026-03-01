import os
from sqlalchemy import create_engine, text
import pandas as pd
import statistics
from performance_tracker import INITIAL_EQUITY

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# =========================
# CONFIG
# =========================

BASE_RISK_CAP = 0.03
DEFAULT_RISK = 0.02
MAX_DRAWDOWN_LIMIT = 12
EQUITY_MA_PERIOD = 20
REGIME_LOOKBACK = 30


# =========================
# EQUITY DATA
# =========================

def get_equity_data():

    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT profit FROM trades ORDER BY created_at ASC",
            conn
        )

    equity = INITIAL_EQUITY
    equity_series = [equity]

    for p in df["profit"]:
        equity += p
        equity_series.append(equity)

    equity_df = pd.DataFrame({"equity": equity_series})

    peak = equity_df["equity"].cummax().iloc[-1]
    current_equity = equity_df["equity"].iloc[-1]
    drawdown = (peak - current_equity) / peak * 100 if peak > 0 else 0

    return current_equity, peak, drawdown, equity_df, df


# =========================
# DRAWDOWN TIERS
# =========================

def drawdown_multiplier(drawdown):

    if drawdown < 1:
        return 1.00
    elif drawdown < 3:
        return 0.85
    elif drawdown < 5:
        return 0.65
    elif drawdown < 8:
        return 0.45
    elif drawdown < 12:
        return 0.25
    else:
        return 0.0


# =========================
# KELLY (Half Kelly)
# =========================

def calculate_kelly(trade_df):

    if trade_df.empty:
        return DEFAULT_RISK

    wins = trade_df[trade_df["profit"] > 0]
    losses = trade_df[trade_df["profit"] <= 0]

    if losses.empty:
        return DEFAULT_RISK

    win_rate = len(wins) / len(trade_df)
    avg_win = wins["profit"].mean()
    avg_loss = abs(losses["profit"].mean())

    if avg_loss == 0:
        return DEFAULT_RISK

    R = avg_win / avg_loss
    kelly = win_rate - ((1 - win_rate) / R)

    half_kelly = max(kelly / 2, 0)

    return min(half_kelly, BASE_RISK_CAP)


# =========================
# EQUITY MOMENTUM (EMA)
# =========================

def equity_momentum_multiplier(equity_df):

    if len(equity_df) < EQUITY_MA_PERIOD:
        return 1.0

    equity_df["ema"] = equity_df["equity"].ewm(
        span=EQUITY_MA_PERIOD,
        adjust=False
    ).mean()

    current_equity = equity_df["equity"].iloc[-1]
    current_ema = equity_df["ema"].iloc[-1]

    return 1.0 if current_equity >= current_ema else 0.5


# =========================
# INTERNAL VOLATILITY
# =========================

def volatility_multiplier(trade_df):

    if len(trade_df) < 10:
        return 1.0

    returns = trade_df["profit"].pct_change().dropna()

    if len(returns) < 2:
        return 1.0

    vol = statistics.stdev(returns)

    if vol < 0.01:
        return 1.0
    elif vol < 0.02:
        return 0.9
    elif vol < 0.03:
        return 0.8
    else:
        return 0.6


# =========================
# REGIME DETECTION
# =========================

def regime_multiplier(equity_df, trade_df):

    if len(equity_df) < REGIME_LOOKBACK:
        return 1.0

    recent_equity = equity_df["equity"].iloc[-REGIME_LOOKBACK:]
    slope = recent_equity.iloc[-1] - recent_equity.iloc[0]

    recent_trades = trade_df.iloc[-REGIME_LOOKBACK:]

    if recent_trades.empty:
        return 1.0

    win_rate = len(recent_trades[recent_trades["profit"] > 0]) / len(recent_trades)

    returns = recent_trades["profit"].pct_change().dropna()
    vol = statistics.stdev(returns) if len(returns) > 1 else 0

    # Trend Mode
    if slope > 0 and win_rate > 0.6 and vol < 0.02:
        return 1.1

    # Defensive Mode
    if slope < 0 or win_rate < 0.5 or vol > 0.03:
        return 0.6

    # Neutral
    return 1.0


# =========================
# POSITION SIZE ENGINE
# =========================

def calculate_position_size(stop_distance, external_volatility=None):

    if stop_distance <= 0:
        return 0

    equity, peak, drawdown, equity_df, trade_df = get_equity_data()

    if drawdown >= MAX_DRAWDOWN_LIMIT:
        raise Exception("❌ Trading frozen due to high drawdown.")

    kelly_risk = calculate_kelly(trade_df)
    dd_factor = drawdown_multiplier(drawdown)
    recovery_factor = equity / peak if peak > 0 else 1
    momentum_factor = equity_momentum_multiplier(equity_df)
    vol_factor = volatility_multiplier(trade_df)
    regime_factor = regime_multiplier(equity_df, trade_df)

    # External volatility param
    if external_volatility is not None:
        if external_volatility < 0.01:
            external_vol_mult = 1.0
        elif external_volatility < 0.02:
            external_vol_mult = 0.9
        elif external_volatility < 0.03:
            external_vol_mult = 0.8
        else:
            external_vol_mult = 0.6
    else:
        external_vol_mult = 1.0

    dynamic_risk = (
        kelly_risk *
        dd_factor *
        recovery_factor *
        momentum_factor *
        vol_factor *
        regime_factor *
        external_vol_mult
    )

    dynamic_risk = min(dynamic_risk, BASE_RISK_CAP)

    risk_amount = equity * dynamic_risk
    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# =========================
# TRADE LOGGER
# =========================

def log_trade(symbol, side, entry_price, exit_price, quantity):

    equity, peak, drawdown, _, _ = get_equity_data()

    if drawdown >= MAX_DRAWDOWN_LIMIT:
        raise Exception("❌ Trading frozen due to drawdown.")

    if side.lower() == "long":
        profit = (exit_price - entry_price) * quantity
    else:
        profit = (entry_price - exit_price) * quantity

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO trades
            (symbol, side, entry_price, exit_price, quantity, profit)
            VALUES
            (:symbol, :side, :entry_price, :exit_price, :quantity, :profit)
        """), {
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "profit": profit
        })
        conn.commit()

    return round(profit, 2)
