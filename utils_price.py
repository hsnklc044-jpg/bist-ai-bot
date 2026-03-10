def safe_float(value):

    try:

        if hasattr(value, "iloc"):
            return float(value.iloc[-1])

        return float(value)

    except:

        return 0.0