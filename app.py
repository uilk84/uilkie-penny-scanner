import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import pytz

st.set_page_config(page_title="Uilkie Chaos Engine v3", layout="wide")
st.title("🚀 Uilkie Penny Lotto Chaos Engine v3")

API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    st.error("Missing POLYGON_API_KEY")
    st.stop()

eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)
today = now.strftime("%Y-%m-%d")

# -----------------------------
# SNAPSHOT UNIVERSE
# -----------------------------

snapshot_url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={API_KEY}"
r = requests.get(snapshot_url)
tickers_data = r.json().get("tickers", [])

if not tickers_data:
    st.warning("No snapshot data available.")
    st.stop()

# Filter lotto universe
candidates = []

for t in tickers_data:
    try:
        price = t["lastTrade"]["p"]
        volume = t["day"]["v"]

        if 0.20 <= price <= 5 and volume > 300000:
            candidates.append(t["ticker"])
    except:
        continue

candidates = candidates[:30]

if not candidates:
    st.info("No lotto candidates right now.")
    st.stop()

# -----------------------------
# BREAKOUT + ACCELERATION ENGINE
# -----------------------------

chaos_hits = []

for ticker in candidates:

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
st.caption("Uilkie Alpha Fund | Snapshot + 5m Breakout Engine")
