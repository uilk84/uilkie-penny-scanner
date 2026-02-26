import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("FULL PENNY LOTTO CHAOS MODE | Under $5 | High Momentum")

API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    st.error("Polygon API key not found.")
    st.stop()

if st.button("Run Lotto Scan"):

    url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={API_KEY}"

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
            prev_close = t["prevDay"]["c"]
            volume = t["day"]["v"]

            if prev_close == 0:
                continue

            percent_change = ((price - prev_close) / prev_close) * 100

            # 🔥 CHAOS FILTER
            if price < 5 and percent_change > 3:
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
        st.dataframe(df.head(50))
    else:
        st.warning("No penny lotto runners detected right now.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Chaos Mode | Polygon Snapshot API")
