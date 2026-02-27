import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import pytz

st.set_page_config(page_title="Uilkie Lotto Hybrid", layout="wide")

st.title("🚀 Uilkie Penny Lotto Hybrid Scanner")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

if not POLYGON_API_KEY:
    st.error("Missing POLYGON_API_KEY")
    st.stop()

# ----------------------------
# Time Detection
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
# Pull Snapshot
# ----------------------------

url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={POLYGON_API_KEY}"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
except:
    st.error("Polygon API request failed.")
    st.stop()

tickers = data.get("tickers", [])

if not tickers:
    st.warning("No data returned from Polygon.")
    st.stop()

results = []

for t in tickers:
    try:
        ticker = t.get("ticker")
        last_trade = t.get("lastTrade", {})
        prev_day = t.get("prevDay", {})
        day_data = t.get("day", {})

        last_price = last_trade.get("p")
        prev_close = prev_day.get("c")
        volume = day_data.get("v", 0)

        if not last_price or not prev_close or prev_close == 0:
            continue

        percent_change = ((last_price - prev_close) / prev_close) * 100

        results.append({
            "Ticker": ticker,
            "Price": round(last_price, 3),
            "PercentChange": round(percent_change, 2),
            "Volume": volume
        })

    except:
        continue

if not results:
    st.warning("No valid ticker data processed.")
    st.stop()

df = pd.DataFrame(results)

# Safe sort
if "PercentChange" in df.columns:
    df = df.sort_values(by="PercentChange", ascending=False)
else:
    st.warning("PercentChange column missing.")
    st.stop()

# ----------------------------
# FILTER LOGIC
# ----------------------------

filtered = df[
    (df["Price"] >= 0.20) &
    (df["Price"] <= 10) &
    (df["Volume"] > 100000)
]

if is_premarket:
    st.warning("🟡 Premarket Mode")
elif is_market_open:
    st.success("🟢 Market Open")
else:
    st.info("🔵 After Hours")

if not filtered.empty:
    st.dataframe(filtered.head(20))
else:
    st.info("No momentum setups found.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Stable Hybrid Build")
