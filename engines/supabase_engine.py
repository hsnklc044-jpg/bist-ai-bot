from supabase import create_client

SUPABASE_URL = "https://llwdcvmjztoowqxiqkzm.supabase.co"
SUPABASE_KEY = "sb_publishable_1yTQJ0lDD9WBkTmRTCgDSw_f4vyt6bu"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_signal(symbol, signal, score, price):

    data = {
        "symbol": symbol,
        "signal": signal,
        "score": score,
        "price": price
    }

    supabase.table("signals").insert(data).execute()