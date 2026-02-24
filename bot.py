import os
import requests
import pandas as pd
import yfinance as yf
import numpy as np
from flask import Flask
from threading import Thread
import time
import traceback

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RISK_PER_TRADE = 0.01
PORTFOLIO_SIZE = 100000

app = Flask(__name__)

# =====================================================
# TELEGRAM
# =====================================================

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Env variables missing")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# =====================================================
# DATA ENGINE
# =====================================================

def get_data(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

# =====================================================
# SIMPLE SAFE SCAN (stabil versiyon)
# =====================================================

def run_scan():
    print("Scan running")
    send_telegram("🤖 Bot aktif - sistem stabil.")

# =====================================================
# BACKGROUND LOOP
# =====================================================

def scheduler():
    while True:
        try:
            run_scan()
        except Exception:
            print(traceback.format_exc())
        time.sleep(3600)

# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/")
def home():
    return "BIST BOT ACTIVE"

# =====================================================
# START
# =====================================================

def start_background():
    Thread(target=scheduler, daemon=True).start()

start_background()
