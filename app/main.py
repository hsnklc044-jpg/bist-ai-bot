from datetime import datetime

@app.get("/send_report")
def send_report():

    # UTC zamanı al
    now = datetime.utcnow()

    # Türkiye UTC+3
    turkey_hour = (now.hour + 3) % 24
    minute = now.minute

    # Sadece 09:54–09:56 arası çalışsın
    if not (turkey_hour == 9 and 54 <= minute <= 56):
        return {"status": "Saat dışı - Rapor gönderilmedi"}

    result = scan_market()
    pge = result["piyasa_guc_endeksi"]

    if pge < 30:
        yorum = "⚠️ Piyasa Zayıf – Riskli Bölge"
    elif pge < 50:
        yorum = "⏳ Piyasa Nötr – Geçiş Aşaması"
    elif pge < 70:
        yorum = "💪 Piyasa Güçlü – Trend Başlıyor"
    else:
        yorum = "🚀 Piyasa Çok Güçlü – Momentum Fazı"

    tum_hisseler = (
        result["breakout"] +
        result["trend"] +
        result["dip"]
    )

    tum_hisseler = sorted(tum_hisseler, key=lambda x: x["score"], reverse=True)
    top3 = tum_hisseler[:3]

    mesaj = f"""
📊 BIST AI PRO RAPOR

📈 Piyasa Güç Endeksi: %{pge}
🧠 {yorum}

🚀 Breakout: {result['breakout_sayisi']}
📈 Trend: {result['trend_sayisi']}
🔄 Dip: {result['dip_sayisi']}

🏆 EN GÜÇLÜ 3 HİSSE
"""

    for hisse in top3:
        mesaj += f"""
{hisse['symbol']}
Fiyat: {hisse['close']}
RSI: {hisse['rsi']}
Skor: {hisse['score']}
------------------
"""

    mesaj += "\n🤖 BIST AI BOT"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj
    }

    requests.post(url, data=payload)

    return {"status": "Telegram Gönderildi"}
