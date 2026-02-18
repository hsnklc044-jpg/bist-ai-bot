async def rapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Günlük tarama başlatıldı...")

    try:
        from ai_signal_engine import run_daily_scan
        sonuc = run_daily_scan()
        await update.message.reply_text(f"SONUÇ:\n{sonuc}")
    except Exception as e:
        await update.message.reply_text(f"HATA:\n{e}")
