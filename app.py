import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import pytz
import numpy as np

st.set_page_config(page_title="Uilkie Chaos Engine", layout="wide")
st.title("🚀 Uilkie Penny Lotto Chaos Engine")

API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    st.error("Missing POLYGON_API_KEY")
    st.stop()

# -----------------------------
# TIME (Eastern)
# -----------------------------

eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)

today = now.strftime("%Y-%m-%d")

# -----------------------------
# STEP 1: Get full market daily data
# -----------------------------

grouped_url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{today}?adjusted=true&apiKey={API_KEY}"

try:
    r = requests.get(grouped_url, timeout=10)
    data = r.json()
except:
    st.error("Failed pulling grouped data")
    st.stop()

results = data.get("results", [])

if not results:
    st.warning("No grouped data available (market closed or early).")
    st.stop()

df = pd.DataFrame(results)

# Rename columns for clarity
df = df.rename(columns={
    "T": "Ticker",
    "c": "Close",
    "o": "Open",
    "h": "High",
    "l": "Low",
    "v": "Volume"
})

# Basic lotto filter
df = df[
    (df["Close"] >= 0.20) &
    (df["Close"] <= 5) &
    (df["Volume"] > 300000)
]

if df.empty:
    st.info("No lotto candidates from daily filter.")
    st.stop()

tickers = df["Ticker"].tolist()[:25]  # Limit for speed

# -----------------------------
# STEP 2: Intraday Breakout Logic
# -----------------------------

chaos_hits = []

for ticker in tickers:
    intraday_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/5/minute/{today}/{today}?adjusted=true&apiKey={API_KEY}"

    try:
        r = requests.get(intraday_url, timeout=5)
        intraday_data = r.json().get("results", [])
    except:
        continue

    if not intraday_data or len(intraday_data) < 10:
        continue

    intraday_df = pd.DataFrame(intraday_data)

    intraday_df = intraday_df.rename(columns={
        "c": "Close",
        "o": "Open",
        "h": "High",
        "l": "Low",
        "v": "Volume"
    })

    # Calculate volume acceleration
    intraday_df["AvgVol"] = intraday_df["Volume"].rolling(5).mean()

    latest = intraday_df.iloc[-1]
    previous = intraday_df.iloc[:-1]

    # Breakout = new intraday high
    breakout = latest["High"] > previous["High"].max()

    # Volume acceleration
    vol_spike = latest["Volume"] > (latest["AvgVol"] * 3)

    # Strong expansion candle
    expansion = (latest["Close"] - latest["Open"]) / latest["Open"] > 0.04

    if breakout and vol_spike and expansion:
        chaos_hits.append({
            "Ticker": ticker,
            "Price": round(latest["Close"], 3),
            "5m % Move": round(((latest["Close"] - latest["Open"]) / latest["Open"]) * 100, 2),
            "Volume": int(latest["Volume"])
        })

# -----------------------------
# DISPLAY RESULTS
# -----------------------------

if chaos_hits:
    chaos_df = pd.DataFrame(chaos_hits)
    st.success("🔥 CHAOS BREAKOUT DETECTED")
    st.dataframe(chaos_df)
else:
    st.info("No chaos breakouts detected right now.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Breakout + Volume Acceleration Engine")
