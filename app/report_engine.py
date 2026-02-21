def generate_report(scan_data):

    pge = scan_data["piyasa_guc_endeksi"]
    durum = scan_data["durum"]

    breakout = scan_data["breakout"]
    trend = scan_data["trend"]
    dip = scan_data["dip"]

    message = f"""
📊 *BIST AI Günlük Rapor*

PGE: *{pge}* ({durum})

🔴 Breakout: {len(breakout)}
🟡 Trend: {len(trend)}
🔵 Dip: {len(dip)}
"""

    if trend:
        message += "\n\n🔥 *En Güçlü 3 Trend*\n"
        for i, item in enumerate(trend[:3], start=1):
            message += f"{i}. {item['symbol']} – Skor {item['score']}\n"

    return message
