import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("PRO MODE | Intraday Expansion + Active Momentum")

API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    st.error("Polygon API key not found.")
    st.stop()

if st.button("Run Pro Lotto Scan"):

    today = datetime.now().strftime("%Y-%m-%d")

    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{today}?adjusted=true&apiKey={API_KEY}"

    response = requests.get(url)
    data = response.json()
    stocks = data.get("results", [])

    results = []

    for stock in stocks:
        try:
            ticker = stock["T"]
            open_price = stock["o"]
            high = stock["h"]
            close = stock["c"]
            prev_close = stock["p"]   # previous close
            volume = stock["v"]

            if prev_close == 0:
                continue

            spike_percent = ((high - prev_close) / prev_close) * 100
            active_percent = ((close - prev_close) / prev_close) * 100

            # 🔥 PRO HYBRID FILTER
            if (
                close < 5 and
                spike_percent > 20 and
                active_percent > 5 and
                volume > 300000
            ):
                results.append({
                    "Ticker": ticker,
                    "Price": round(close, 3),
                    "Spike %": round(spike_percent, 2),
                    "Current %": round(active_percent, 2),
                    "Volume": volume
                })

        except:
            continue

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="Spike %", ascending=False)

        st.success(f"🔥 Found {len(df)} Active Penny Runners")
        st.dataframe(df.head(50))
    else:
        st.warning("No active penny runners detected right now.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Professional Hybrid Momentum Scanner")
