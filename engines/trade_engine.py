from supabase_engine import supabase


def open_trade(symbol, strategy, price):

    data = {
        "symbol": symbol,
        "strategy": strategy,
        "entry_price": price,
        "status": "OPEN"
    }

    supabase.table("trades").insert(data).execute()