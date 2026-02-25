import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ----------------------------------
# Page Setup
# ----------------------------------

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("Live Momentum Mode | Price < $10 | Batch API Version")

# ----------------------------------
# Ticker Universe (Expand Later)
# ----------------------------------

TICKERS = [
    "AAPL","MSFT","NVDA","AMD","TSLA","PLTR","SOFI","LCID","RIVN",
    "F","T","NIO","BB","AMC","GME","MARA","RIOT","NKLA","OPEN",
    "HOOD","QS","UPST","AFRM","SNDL","TLRY","MULN","BBIG",
    "XPEV","CHPT","WKHS","CLOV","SPCE","PENN","RUN"
]

# ----------------------------------
# RSI Function
# ----------------------------------

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ----------------------------------
# Scanner
# ----------------------------------

if st.button("Run Lotto Scan"):

    results = []

    try:
        data = yf.download(
            TICKERS,
            period="5d",
            interval="1d",
            group_by="ticker",
            progress=False
        )
    except:
        st.error("Data download failed.")
        st.stop()

    for ticker in TICKERS:
        try:
            df = data[ticker]

            if df.empty or len(df) < 2:
                continue

            price = df["Close"].iloc[-1]
            prev_close = df["Close"].iloc[-2]

            if price > 10:
                continue

            percent_change = ((price - prev_close) / prev_close) * 100

            if percent_change < 3:
                continue

            rsi = calculate_rsi(df["Close"]).iloc[-1]

            if rsi > 45:
                results.append({
                    "Ticker": ticker,
                    "Price": round(float(price), 2),
                    "% Change": round(float(percent_change), 2),
                    "RSI": round(float(rsi), 2),
                    "Signal": "🚀 MOMENTUM GAINER"
                })

        except:
            continue

    if results:
        df_results = pd.DataFrame(results).sort_values(by="% Change", ascending=False)
        st.success(f"Found {len(results)} momentum setups")
        st.dataframe(df_results)
    else:
        st.warning("No momentum setups found.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Stable Batch Scanner")
