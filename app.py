import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import pytz

st.set_page_config(page_title="Uilkie Penny Lotto Hybrid", layout="wide")

st.title("🚀 Uilkie Penny Lotto Hybrid Scanner")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not POLYGON_API_KEY:
    st.error("Missing POLYGON_API_KEY")
    st.stop()

# ----------------------------
# Time Detection (Eastern)
# ----------------------------

eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)

premarket_start = now.replace(hour=4, minute=0, second=0)
market_open = now.replace(hour=9, minute=30, second=0)
market_close = now.replace(hour=16, minute=0, second=0)

is_premarket = premarket_start <= now < market_open
is_market_open = market_open <= now <= market_close
is_after_hours = now > market_close

# ----------------------------
# Telegram Sender
# ----------------------------

def send_telegram(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload)

# ----------------------------
# Pull Snapshot Data (Works All Sessions)
# ----------------------------

snapshot_url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={POLYGON_API_KEY}"

response = requests.get(snapshot_url)
data = response.json()
tickers = data.get("tickers", [])

results = []

for t in tickers:
    try:
        ticker = t["ticker"]
        last_price = t["lastTrade"]["p"]
        prev_close = t["prevDay"]["c"]
        volume = t["day"]["v"]

        if prev_close == 0:
            continue

        percent_change = ((last_price - prev_close) / prev_close) * 100

        results.append({
            "Ticker": ticker,
            "Price": round(last_price, 3),
            "% Change": round(percent_change, 2),
            "Volume": volume
        })

    except:
        continue

df = pd.DataFrame(results)
df = df.sort_values(by="% Change", ascending=False)

# ----------------------------
# PREMARKET MODE
# ----------------------------

if is_premarket:
    st.warning("🟡 Premarket Mode Active (4:00–9:30 ET)")

    premarket_setups = df[
        (df["Price"] >= 0.20) &
        (df["Price"] <= 10) &
        (df["% Change"] > 8) &
        (df["Volume"] > 100000)
    ]

    if not premarket_setups.empty:
        st.dataframe(premarket_setups.head(20))

        for _, row in premarket_setups.head(5).iterrows():
            send_telegram(
                f"🟡 PREMARKET RUNNER\n"
                f"{row['Ticker']}\n"
                f"Price: {row['Price']}\n"
                f"% Change: {row['% Change']}%\n"
                f"Volume: {row['Volume']}"
            )
    else:
        st.info("No significant premarket runners yet.")

# ----------------------------
# REGULAR SESSION MODE
# ----------------------------

elif is_market_open:
    st.success("🟢 Regular Market Session Active")

    live_setups = df[
        (df["Price"] >= 0.20) &
        (df["Price"] <= 10) &
        (df["% Change"] > 5) &
        (df["Volume"] > 500000)
    ]

    if not live_setups.empty:
        st.dataframe(live_setups.head(20))

        for _, row in live_setups.head(5).iterrows():
            send_telegram(
                f"🚨 LIVE RUNNER\n"
                f"{row['Ticker']}\n"
                f"Price: {row['Price']}\n"
                f"% Change: {row['% Change']}%\n"
                f"Volume: {row['Volume']}"
            )
    else:
        st.info("No strong intraday runners right now.")

# ----------------------------
# AFTER HOURS MODE
# ----------------------------

else:
    st.info("🔵 After Hours — Showing Top Movers From Today")

    st.dataframe(df.head(20))

st.markdown("---")
st.caption("Uilkie Alpha Fund | 3-Session Hybrid Momentum Scanner")
