import yfinance as yf
import pandas as pd
import traceback


def analyze_stock(symbol):

    try:

        df = yf.download(
            symbol,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):

            close = df["Close"].iloc[:, 0]
            high = df["High"].iloc[:, 0]
            low = df["Low"].iloc[:, 0]
            volume = df["Volume"].iloc[:, 0]

        else:

            close = df["Close"]
            high = df["High"]
            low = df["Low"]
            volume = df["Volume"]

        # NaN temizliği

        price_df = pd.DataFrame({
            "close": close,
            "high": high,
            "low": low,
            "volume": volume
        }).dropna()

        if price_df.empty:
            return None

        close = price_df["close"]
        high = price_df["high"]
        low = price_df["low"]
        volume = price_df["volume"]

        if len(close) < 50:
            return None

        current_price = round(
            float(close.iloc[-1]),
            2
        )

        ma20 = round(
            float(
                close.rolling(20).mean().iloc[-1]
            ),
            2
        )

        ma50 = round(
            float(
                close.rolling(50).mean().iloc[-1]
            ),
            2
        )

        # RSI

        delta = close.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        avg_gain_last = avg_gain.iloc[-1]
        avg_loss_last = avg_loss.iloc[-1]

        if pd.isna(avg_gain_last) or pd.isna(avg_loss_last):

            rsi = 50

        elif avg_loss_last == 0:

            rsi = 100

        else:

            rs = avg_gain_last / avg_loss_last

            rsi = (
                100 -
                (100 / (1 + rs))
            )

        rsi = round(
            float(rsi),
            2
        )

        # MACD

        ema12 = close.ewm(
            span=12,
            adjust=False
        ).mean()

        ema26 = close.ewm(
            span=26,
            adjust=False
        ).mean()

        macd = ema12.iloc[-1] - ema26.iloc[-1]

        if pd.isna(macd):
            macd = 0

        macd = round(
            float(macd),
            2
        )

        # Volume

        avg_volume = volume.rolling(20).mean().iloc[-1]

        if pd.isna(avg_volume) or avg_volume <= 0:

            volume_ratio = 1

        else:

            volume_ratio = round(
                float(volume.iloc[-1]) /
                float(avg_volume),
                2
            )

        # Volatility

        volatility = close.pct_change(
            fill_method=None
        ).std()

        if pd.isna(volatility):

            volatility = 0

        else:

            volatility = round(
                float(volatility * 100),
                2
            )

        # ATR

        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()

        tr = pd.concat(
            [tr1, tr2, tr3],
            axis=1
        ).max(axis=1)

        atr = tr.rolling(
            14,
            min_periods=1
        ).mean().iloc[-1]

        if pd.isna(atr):
            atr = current_price * 0.03

        atr = round(
            float(atr),
            2
        )

        # =====================
        # SCORE ENGINE V32
        # =====================

        bull_score = 0
        bear_score = 0

        # Trend

        if ma20 > ma50:
            bull_score += 25
        else:
            bear_score += 25

        # RSI

        if rsi < 30:
            bull_score += 20

        elif rsi < 40:
            bull_score += 10

        elif rsi > 80:
            bear_score += 15

        elif rsi > 70:
            bear_score += 10

        # MACD

        if macd > 0:
            bull_score += 15
        else:
            bear_score += 15

        # Volume

        if volume_ratio > 1.1:
            bull_score += 10

        elif volume_ratio < 0.8:
            bear_score += 10

        # Volatility

        if volatility < 2:
            bull_score += 10

        elif volatility > 6:
            bear_score += 10

        raw_score = bull_score - bear_score

        score = 50 + (raw_score * 0.5)

        score = round(
            max(
                0,
                min(score, 100)
            ),
            0
        )

        # SIGNALS

        signal = "WATCH"
        trend = "SIDEWAYS"

        if score >= 80:

            signal = "STRONG BUY"
            trend = "BULLISH"

        elif score >= 70:

            signal = "BUY"
            trend = "BULLISH"

        elif score <= 20:

            signal = "STRONG SELL"
            trend = "BEARISH"

        elif score <= 35:

            signal = "SELL"
            trend = "BEARISH"

        # CONFIDENCE

        confidence = min(
            100,
            max(
                0,
                int(
                    score * 0.85 +
                    volume_ratio * 8
                )
            )
        )

        # TRADE LEVELS

        entry_price = current_price

        stop_loss = round(
            current_price - (atr * 2),
            2
        )

        target_1 = round(
            current_price + (atr * 2),
            2
        )

        target_2 = round(
            current_price + (atr * 4),
            2
        )

        return {

            "symbol": symbol,
            "price": current_price,

            "score": score,
            "trend": trend,
            "signal": signal,

            "confidence": confidence,

            "rsi": rsi,
            "macd": macd,

            "volume_ratio": volume_ratio,
            "volatility": volatility,

            "bull_score": bull_score,
            "bear_score": bear_score,

            "atr": atr,

            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,

            "ma20": ma20,
            "ma50": ma50
        }

    except Exception:

        print(f"\n[AI ERROR] {symbol}")
        traceback.print_exc()

        return None