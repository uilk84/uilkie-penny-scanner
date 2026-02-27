import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import pytz

st.set_page_config(page_title="Uilkie Chaos Engine (Free Mode)", layout="wide")
st.title("🚀 Uilkie Penny Lotto Chaos Engine — Free Mode")

API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    st.error("Missing POLYGON_API_KEY")
    st.stop()

eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)
today = now.strftime("%Y-%m-%d")

# -----------------------------
# STEP 1: Get Top Gainers
# -----------------------------

gainers_url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/gainers?apiKey={API_KEY}"
r = requests.get(gainers_url)

if r.status_code != 200:
    st.error("Failed to pull top gainers.")
    st.write(r.text)
    st.stop()

gainers = r.json().get("tickers", [])

if not gainers:
    st.info("No gainers returned.")
    st.stop()

# Filter under $5
candidates = []

for g in gainers:
    try:
        price = g["lastTrade"]["p"]
        if 0.20 <= price <= 5:
            candidates.append(g["ticker"])
    except:
        continue

if not candidates:
    st.info("No lotto candidates among gainers.")
    st.stop()

# -----------------------------
# STEP 2: Breakout Engine
# -----------------------------

chaos_hits = []

for ticker in candidates[:20]:

    intraday_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/5/minute/{today}/{today}?adjusted=true&apiKey={API_KEY}"
    r = requests.get(intraday_url)
    bars = r.json().get("results", [])

    if not bars or len(bars) < 6:
        continue

    df = pd.DataFrame(bars)
    df = df.rename(columns={"c":"Close","o":"Open","h":"High","v":"Volume"})
    df["AvgVol"] = df["Volume"].rolling(5).mean()

    latest = df.iloc[-1]
    previous = df.iloc[:-1]

    breakout = latest["High"] > previous["High"].max()
    vol_spike = latest["Volume"] > (latest["AvgVol"] * 3)
    expansion = (latest["Close"] - latest["Open"]) / latest["Open"] > 0.03

    if breakout and vol_spike and expansion:
        chaos_hits.append({
            "Ticker": ticker,
            "Price": round(latest["Close"], 3),
            "5m Move %": round(((latest["Close"] - latest["Open"]) / latest["Open"]) * 100, 2),
            "Volume": int(latest["Volume"])
        })

# -----------------------------
# DISPLAY
# -----------------------------

if chaos_hits:
    st.success("🚨 CHAOS BREAKOUT DETECTED")
    st.dataframe(pd.DataFrame(chaos_hits))
else:
    st.info("No confirmed breakouts right now.")

st.markdown("---")
st.caption("Free Plan Mode | Scanning Top Gainers Only")
