def check_liquidity(df):

    try:

        avg_volume = df["Volume"].rolling(30).mean().iloc[-1]

        current_volume = df["Volume"].iloc[-1]

        price = df["Close"].iloc[-1]

        # yaklaşık günlük TL hacim
        daily_value = current_volume * price

        if avg_volume < 300000:
            return False

        if daily_value < 50_000_000:
            return False

        return True

    except Exception as e:

        print("Liquidity error:", e)

        return False
