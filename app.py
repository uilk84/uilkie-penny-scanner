import streamlit as st
import requests
import pandas as pd
import os

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("FULL PENNY LOTTO CHAOS MODE | Under $5 | Polygon Gainers Endpoint")

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

    url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/gainers?apiKey={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()
        tickers = data.get("tickers", [])
    except:
        st.error("Polygon API request failed.")
        st.stop()

    results = []

    for t in tickers:
        try:
            price = t["lastTrade"]["p"]
            percent_change = t.get("todaysChangePerc", 0)
            volume = t["day"]["v"]

            # 🔥 CHAOS FILTER
            if price < 5:
                results.append({
                    "Ticker": t["ticker"],
                    "Price": round(price, 3),
                    "% Change": round(percent_change, 2),
                    "Volume": volume
                })

        except:
            continue

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="% Change", ascending=False)

        st.success(f"🔥 Found {len(df)} Penny Lotto Movers")
        st.dataframe(df)
    else:
        st.warning("No penny lotto runners detected right now.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Chaos Mode | Polygon Gainers API")
