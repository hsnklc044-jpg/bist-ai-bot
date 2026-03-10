# 🚀 BIST AI Telegram Bot

BIST30 hisselerini tarayan ve RSI tabanlı teknik analiz ile sinyal üreten
minimal Telegram bildirim botudur.

----------------------------------------

## 📌 Özellikler

- BIST30 otomatik tarama
- RSI bazlı alım sinyali
- Skor hesaplama
- En iyi 3 hisse seçimi
- Telegram’a otomatik mesaj gönderimi
- Background Worker olarak çalışır

----------------------------------------

## 🧠 Sistem Akışı

main.py
→ scanner.py
→ strategy.py
→ scoring_engine.py
→ telegram_sender.py

----------------------------------------

## ⚙️ Kurulum

### 1) Environment Variables (Render)

Render üzerinde aşağıdaki değişkenleri ekleyin:

TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID

----------------------------------------

### 2) Render Ayarları

Service Type:
Background Worker

Start Command:
python bot.py

----------------------------------------

## 📂 Proje Yapısı

root/
│
├── bot.py
├── requirements.txt
├── runtime.txt
│
└── app/
    ├── __init__.py
    ├── main.py
    ├── scanner.py
    ├── strategy.py
    ├── scoring_engine.py
    ├── data_utils.py
    ├── telegram_sender.py
    └── bist30.py

----------------------------------------

## 🔔 Çalışma Mantığı

1. BIST30 hisseleri çekilir
2. Son 3 aylık veri indirilir
3. RSI hesaplanır
4. RSI < 30 olanlar filtrelenir
5. Skor hesaplanır
6. En iyi 3 hisse Telegram’a gönderilir

----------------------------------------

## ⚠️ Uyarı

Bu sistem yatırım tavsiyesi değildir.
Sadece teknik filtreleme ve otomasyon amaçlıdır.

----------------------------------------

Minimal Stable Build
