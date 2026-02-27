import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import time

st.set_page_config(page_title="Uilkie Penny Lotto Auto Alert", layout="wide")

st.title("🚀 Uilkie Penny Lotto Auto Alert System")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not POLYGON_API_KEY:
    st.error("Missing POLYGON_API_KEY")
    st.stop()

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    st.error("Missing Telegram credentials")
    st.stop()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

def scan_market():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{today}?adjusted=true&apiKey={POLYGON_API_KEY}"

    response = requests.get(url)
    data = response.json()
    stocks = data.get("results", [])

    alerts = []

    for stock in stocks:
        try:
            ticker = stock["T"]
            open_price = stock["o"]
            high = stock["h"]
            close = stock["c"]
            prev_close = stock["p"]
            volume = stock["v"]

            if prev_close == 0:
                continue

            change_from_open = ((close - open_price) / open_price) * 100

            if (
                0.20 <= close <= 10 and
                volume > 500000 and
                change_from_open > 5
            ):
                alerts.append(
                    f"🚨 {ticker}\n"
                    f"Price: {round(close,2)}\n"
                    f"Change from Open: {round(change_from_open,2)}%\n"
                    f"Volume: {volume}"
                )
        except:
            continue

    return alerts

if st.button("Start Scan Now"):
    alerts = scan_market()

    if alerts:
        for alert in alerts:
            send_telegram(alert)
        st.success(f"Sent {len(alerts)} alerts to Telegram.")
    else:
        st.warning("No setups found right now.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Telegram Alert Mode")
