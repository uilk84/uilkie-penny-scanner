import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Uilkie Signal Tracker Pro", layout="wide")
st.title("📊 Uilkie Signal Tracker Pro")

if "trades" not in st.session_state:
    st.session_state.trades = []

# -------------------------
# Add New Trade
# -------------------------

st.subheader("➕ Add New Signal")

col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Ticker").upper()

with col2:
    entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01)

with col3:
    stop_price = st.number_input("Stop Price", min_value=0.0, step=0.01)

if st.button("Track Signal"):
    if ticker and entry_price > 0 and stop_price > 0 and stop_price < entry_price:
        risk = entry_price - stop_price

        st.session_state.trades.append({
            "Ticker": ticker,
            "Entry": entry_price,
            "Stop": stop_price,
            "Risk": risk,
            "Time": datetime.now(),
            "MaxPrice": entry_price
        })

# -------------------------
# Display Active Trades
# -------------------------

st.subheader("🔥 Active Signals")

if not st.session_state.trades:
    st.info("No signals tracked yet.")
else:
    updated_trades = []

    for trade in st.session_state.trades:
        try:
            data = yf.Ticker(trade["Ticker"])
            hist = data.history(period="1d", interval="1m")

            if hist.empty:
                continue

            current_price = hist["Close"].iloc[-1]
            high_of_day = hist["High"].max()

            # Update max price reached
            trade["MaxPrice"] = max(trade["MaxPrice"], high_of_day)

            pct_move = ((current_price - trade["Entry"]) / trade["Entry"]) * 100
            r_multiple = (current_price - trade["Entry"]) / trade["Risk"]
            max_r = (trade["MaxPrice"] - trade["Entry"]) / trade["Risk"]

            updated_trades.append({
                "Ticker": trade["Ticker"],
                "Entry": trade["Entry"],
                "Stop": trade["Stop"],
                "Current": round(current_price, 3),
                "% Move": round(pct_move, 2),
                "Current R": round(r_multiple, 2),
                "Max R Reached": round(max_r, 2),
                "2R Target": round(trade["Entry"] + trade["Risk"] * 2, 3),
                "3R Target": round(trade["Entry"] + trade["Risk"] * 3, 3),
                "5R Target": round(trade["Entry"] + trade["Risk"] * 5, 3),
                "Tracked At": trade["Time"].strftime("%H:%M:%S")
            })

        except:
            continue

    df = pd.DataFrame(updated_trades)

    if not df.empty:
        df = df.sort_values(by="Max R Reached", ascending=False)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Unable to pull live prices.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | R-Multiple Performance Engine")
