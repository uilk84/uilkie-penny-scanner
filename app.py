import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

# ----------------------------------
# PAGE SETUP
# ----------------------------------

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("FULL MARKET SCAN | Under $5 | Real Momentum Mode")

# ----------------------------------
# LOAD API KEY
# ----------------------------------

API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    st.error("Polygon API key not found. Add POLYGON_API_KEY in Render → Environment.")
    st.stop()

# ----------------------------------
# SCAN BUTTON
# ----------------------------------

if st.button("Run Lotto Scan"):

    today = datetime.now().strftime("%Y-%m-%d")

    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{today}?adjusted=true&apiKey={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()
        results_data = data.get("results", [])
    except:
        st.error("Polygon API request failed.")
        st.stop()

    lotto_results = []

    for stock in results_data:
        try:
            ticker = stock["T"]
            close = stock["c"]
            open_price = stock["o"]
            volume = stock["v"]

            if open_price == 0:
                continue

            percent_change = ((close - open_price) / open_price) * 100

            # 🔥 PENNY LOTTO FILTER
            if close < 5 and percent_change > 2:
                lotto_results.append({
                    "Ticker": ticker,
                    "Price": round(close, 3),
                    "% Change": round(percent_change, 2),
                    "Volume": volume
                })

        except:
            continue

    if lotto_results:
        df = pd.DataFrame(lotto_results)
        df = df.sort_values(by="% Change", ascending=False)

        st.success(f"🔥 Found {len(df)} Penny Lotto Movers")
        st.dataframe(df.head(50))
    else:
        st.warning("No penny lotto runners detected right now.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Full Market Scan | Polygon Grouped Aggregates")
