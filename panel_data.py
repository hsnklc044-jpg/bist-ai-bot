import json
import yfinance as yf
from datetime import datetime

HISSELER = [
    "ASELS.IS", "TUPRS.IS", "KCHOL.IS", "SISE.IS",
    "YKBNK.IS", "AKBNK.IS", "BIMAS.IS", "THYAO.IS",
    "EREGL.IS", "GARAN.IS"
]

sonuclar = []

for hisse in HISSELER:
    try:
        veri = yf.download(hisse, period="6mo")

        if veri.empty:
            continue

        fiyat = float(veri["Close"].iloc[-1])
        degisim = float(
            (veri["Close"].iloc[-1] / veri["Close"].iloc[-20] - 1) * 100
        )

        sonuclar.append({
            "hisse": hisse,
            "fiyat": round(fiyat, 2),
            "degisim": round(degisim, 2)
        })

    except Exception:
        continue


panel = {
    "tarih": datetime.now().strftime("%d-%m-%Y %H:%M"),
    "veriler": sonuclar
}

with open("panel_data.json", "w", encoding="utf-8") as f:
    json.dump(panel, f, ensure_ascii=False, indent=2)

print("panel_data.json oluşturuldu")
