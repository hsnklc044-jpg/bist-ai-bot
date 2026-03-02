async def open_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        capital, risk_percent, _ = get_settings()

        if capital == 0:
            await update.message.reply_text("Önce /setcapital gir.")
            return

        parts = update.message.text.split()
        if len(parts) != 5:
            await update.message.reply_text(
                "❌ Kullanım: /open EREGL long 50 48\n(symbol side entry stop)"
            )
            return

        _, symbol, side, entry, stop = parts

        entry = float(entry)
        stop = float(stop)

        stop_distance = abs(entry - stop)

        if stop_distance == 0:
            await update.message.reply_text("Stop mesafesi 0 olamaz.")
            return

        risk_amount = capital * (risk_percent / 100)
        lot = risk_amount / stop_distance

        # ---- TOPLAM AÇIK RİSK KONTROLÜ ----
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT SUM(ABS(entry - stop) * lot)
        FROM trades
        WHERE status='open';
        """)

        current_risk = cur.fetchone()[0] or 0

        if current_risk + risk_amount > capital * 0.05:
            await update.message.reply_text(
                "🚫 Toplam açık risk limiti (%5) aşılırdı. İşlem açılmadı."
            )
            cur.close()
            conn.close()
            return

        cur.execute("""
        INSERT INTO trades (symbol, side, entry, stop, lot, status)
        VALUES (%s,%s,%s,%s,%s,'open')
        """, (symbol.upper(), side.lower(), entry, stop, lot))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(
            f"""
📥 POZİSYON AÇILDI

{symbol} {side}
Entry: {entry}
Stop: {stop}

🎯 Risk: {round(risk_amount,2)}
📦 Lot: {round(lot,2)}
"""
        )

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Sistem hatası.")
