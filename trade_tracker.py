from supabase_engine import supabase


def open_trade(symbol, signal, price):

    data = {
        "symbol": symbol,
        "signal": signal,
        "entry_price": price,
        "status": "OPEN"
    }

    supabase.table("trades").insert(data).execute()



def close_trade(symbol, price):

    trades = supabase.table("trades").select("*").eq("symbol", symbol).eq("status", "OPEN").execute()

    if not trades.data:
        return

    trade = trades.data[0]

    entry = trade["entry_price"]

    profit = ((price - entry) / entry) * 100

    status = "WIN" if profit > 0 else "LOSS"

    supabase.table("trades").update({

        "exit_price": price,
        "profit": profit,
        "status": status

    }).eq("id", trade["id"]).execute()