import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import pytz
import numpy as np

st.set_page_config(page_title="Uilkie Chaos Engine v2", layout="wide")
st.title("🚀 Uilkie Penny Lotto Chaos Engine v2")

API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    st.error("Missing POLYGON_API_KEY")
    st.stop()

# -----------------------------
# TIME SETUP
# -----------------------------

eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)
today = now.strftime("%Y-%m-%d")

# -----------------------------
# PREMARKET SNAPSHOT (Before 9:30)
# -----------------------------

if now.hour < 9 or (now.hour == 9 and now.minute < 30):

    st.warning("🟡 Premarket Mode")

    snap_url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={API_KEY}"

    r = requests.get(snap_url)
    data = r.json().get("tickers", [])

    results = []

    for t in data:
        try:
            price = t["lastTrade"]["p"]
            prev = t["prevDay"]["c"]
            vol = t["day"]["v"]

            if prev == 0:
                continue

            pct = ((price - prev) / prev) * 100

            if 0.20 <= price <= 5 and pct > 8 and vol > 150000:
                results.append({
                    "Ticker": t["ticker"],
                    "Price": round(price, 3),
                    "%Change": round(pct, 2),
                    "Volume": vol
                })
        except:
            continue

    if results:
        st.success("🔥 Premarket Momentum")
        st.dataframe(pd.DataFrame(results).sort_values("%Change", ascending=False))
    else:
        st.info("No premarket chaos yet.")

# -----------------------------
# MARKET OPEN MODE
# -----------------------------

else:

    st.success("🟢 Market Open — Dual Detection Mode")

    # STEP 1: Daily grouped (universe filter)
    grouped_url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{today}?adjusted=true&apiKey={API_KEY}"
    r = requests.get(grouped_url)
    grouped = r.json().get("results", [])

    if not grouped:
        st.warning("Waiting for official open prints...")
        st.stop()

    df = pd.DataFrame(grouped)
    df = df.rename(columns={"T":"Ticker","c":"Close","v":"Volume"})

    df = df[(df["Close"] >= 0.20) & (df["Close"] <= 5) & (df["Volume"] > 300000)]

    tickers = df["Ticker"].tolist()[:25]

    chaos_hits = []

    for ticker in tickers:

        intraday_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/5/minute/{today}/{today}?adjusted=true&apiKey={API_KEY}"
        r = requests.get(intraday_url)
        bars = r.json().get("results", [])

        if not bars or len(bars) < 6:
            continue

        bars_df = pd.DataFrame(bars)
        bars_df = bars_df.rename(columns={"c":"Close","o":"Open","h":"High","v":"Volume"})

        bars_df["AvgVol"] = bars_df["Volume"].rolling(5).mean()

        latest = bars_df.iloc[-1]
        previous = bars_df.iloc[:-1]

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

    if chaos_hits:
        st.success("🚨 CHAOS BREAKOUT DETECTED")
        st.dataframe(pd.DataFrame(chaos_hits))
    else:
        st.info("No confirmed breakouts yet.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Open Spike + 5m Confirmation Engine")
