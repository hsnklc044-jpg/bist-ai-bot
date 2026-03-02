async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, symbol, side, entry
    FROM trades
    WHERE status='open'
    ORDER BY id;
    """)

    rows = cur.fetchall()

    if not rows:
        await update.message.reply_text("Açık pozisyon yok.")
        return

    msg = "📂 AÇIK POZİSYONLAR\n\n"

    for r in rows:
        msg += f"ID: {r[0]} | {r[1]} {r[2]} @ {r[3]}\n"

    await update.message.reply_text(msg)

    cur.close()
    conn.close()
