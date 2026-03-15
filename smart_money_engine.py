import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from fast_scanner_engine import fast_scan
from scanner_engine import get_top10
from support_engine import support_analysis
from rsi_engine import rsi_scan
from volume_engine import volume_scan
from ai_engine import ai_analyze
from watchlist_engine import generate_watchlist
from smart_money_engine import smart_money_scan

TOKEN = "8772282578:AAHayduiZtDuf659L0Fx9H8ehOcn81tii10"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
message = (
    "🤖 BIST AI Bot\n\n"
    "/scan → Momentum tarama\n"
    "/top10 → Günün güçlü hisseleri\n"
    "/support HİSSE → Destek analizi\n"
    "/rsi → RSI dip hisseler\n"
    "/volume → Hacim patlaması\n"
    "/ai HİSSE → AI analiz\n"
    "/watchlist → Güçlü hisseler\n"
    "/smartmoney → Kurumsal para"
)

await update.message.reply_text(message)
```

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
await update.message.reply_text("⚡ Tarama yapılıyor...")

result = await asyncio.to_thread(fast_scan)

await update.message.reply_text(result)
```

async def top10(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
await update.message.reply_text("📊 Tarama yapılıyor...")

result = await asyncio.to_thread(get_top10)

await update.message.reply_text(result)
```

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
if len(context.args) == 0:
    await update.message.reply_text("Kullanım: /support EREGL")
    return

symbol = context.args[0]

await update.message.reply_text("📉 Destek analizi yapılıyor...")

result = await asyncio.to_thread(support_analysis, symbol)

await update.message.reply_text(result)
```

async def rsi(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
await update.message.reply_text("📉 RSI taraması yapılıyor...")

result = await asyncio.to_thread(rsi_scan)

await update.message.reply_text(result)
```

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
await update.message.reply_text("🔥 Hacim taraması yapılıyor...")

result = await asyncio.to_thread(volume_scan)

await update.message.reply_text(result)
```

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
if len(context.args) == 0:
    await update.message.reply_text("Kullanım: /ai THYAO")
    return

symbol = context.args[0]

await update.message.reply_text("🤖 AI analiz yapılıyor...")

result = await asyncio.to_thread(ai_analyze, symbol)

await update.message.reply_text(result)
```

async def watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
await update.message.reply_text("📊 Watchlist hazırlanıyor...")

result = await asyncio.to_thread(generate_watchlist)

await update.message.reply_text(result)
```

async def smartmoney(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
await update.message.reply_text("🐋 Smart Money taranıyor...")

result = await asyncio.to_thread(smart_money_scan)

await update.message.reply_text(result)
```

def main():

```
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("scan", scan))
app.add_handler(CommandHandler("top10", top10))
app.add_handler(CommandHandler("support", support))
app.add_handler(CommandHandler("rsi", rsi))
app.add_handler(CommandHandler("volume", volume))
app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("watchlist", watchlist))
app.add_handler(CommandHandler("smartmoney", smartmoney))

print("🤖 BIST AI Bot çalışıyor...")

app.run_polling()
```

if **name** == "**main**":
main()
