import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Uilkie Signal Tracker", layout="wide")

st.title("📊 Uilkie Signal Tracker")

if "trades" not in st.session_state:
    st.session_state.trades = []

# -------------------------
# Add New Trade
# -------------------------

st.subheader("➕ Add New Signal")

col1, col2 = st.columns(2)

with col1:
    ticker = st.text_input("Ticker").upper()

with col2:
    entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01)

if st.button("Track Signal"):
    if ticker and entry_price > 0:
        st.session_state.trades.append({
            "Ticker": ticker,
            "Entry": entry_price,
            "Time": datetime.now()
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
            price = data.history(period="1d")["Close"].iloc[-1]

            pct_move = ((price - trade["Entry"]) / trade["Entry"]) * 100

            updated_trades.append({
                "Ticker": trade["Ticker"],
                "Entry": trade["Entry"],
                "Current Price": round(price, 3),
                "% Move": round(pct_move, 2),
                "Tracked At": trade["Time"].strftime("%H:%M:%S")
            })

        except:
            continue

    df = pd.DataFrame(updated_trades)

    if not df.empty:
        df = df.sort_values(by="% Move", ascending=False)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Unable to pull live prices.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Manual Signal Performance Tracker")
