import streamlit as st
import requests
import pandas as pd
import os

# ----------------------------------
# Page Setup
# ----------------------------------

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("Full Market | Polygon Snapshot API | No Scraping")

# ----------------------------------
# Load API Key From Render Environment
# ----------------------------------

API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    st.error("Polygon API key not found. Add POLYGON_API_KEY in Render → Environment.")
    st.stop()

# ----------------------------------
# Scanner
# ----------------------------------

if st.button("Run Lotto Scan"):

    url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()
    except:
        st.error("Polygon API request failed.")
        st.stop()

    tickers = data.get("tickers", [])

    results = []

    for t in tickers:
        try:
            price = t["lastTrade"]["p"]
            prev_close = t["prevDay"]["c"]
            volume = t["day"]["v"]

            percent_change = ((price - prev_close) / prev_close) * 100

            # Filters
            if price < 10 and percent_change > 2 and volume > 200000:
                results.append({
                    "Ticker": t["ticker"],
                    "Price": round(price, 2),
                    "% Change": round(percent_change, 2),
                    "Volume": volume
                })

        except:
            continue

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="% Change", ascending=False)

        st.success(f"Found {len(df)} momentum setups")
        st.dataframe(df.head(25))
    else:
        st.warning("No momentum setups found.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Polygon Powered | Production Mode")
