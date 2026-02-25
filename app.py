import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("NASDAQ + NYSE | Price < $10 | Breakout + Momentum")

# -----------------------------------
# Stable Starter Universe (No URL pulls)
# -----------------------------------

@st.cache_data
def load_tickers():
    return [
        "AAPL","MSFT","NVDA","AMD","TSLA","PLTR","SOFI","LCID","RIVN",
        "F","T","NIO","BB","AMC","GME","MARA","RIOT","NKLA","OPEN",
        "HOOD","QS","UPST","AFRM","SNDL","TLRY","MULN","BBIG",
        "XPEV","CHPT","WKHS","CLOV","SPCE","PENN","RUN"
    ]

tickers = load_tickers()

# -----------------------------------
# RSI Calculation
# -----------------------------------

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# -----------------------------------
# Scanner Logic
# -----------------------------------

results = []

if st.button("Run Lotto Scan"):
    progress = st.progress(0)
    total = len(tickers)

    for i, ticker in enumerate(tickers):
        try:
            df = yf.download(ticker, period="1mo", interval="1d", progress=False)

            if df.empty or len(df) < 20:
                continue

            price = df["Close"].iloc[-1]
            volume = df["Volume"].iloc[-1]

            # Penny filter
            if price > 10 or volume < 500000:
                continue

            # 20-day breakout
            high_20 = df["High"].rolling(20).max().iloc[-2]
            breakout = price > high_20

            # RSI momentum
            rsi = calculate_rsi(df["Close"]).iloc[-1]

            if breakout and rsi > 55:
                results.append({
                    "Ticker": ticker,
                    "Price": round(float(price), 2),
                    "RSI": round(float(rsi), 2),
                    "Volume": int(volume),
                    "Signal": "🚀 LOTTO BREAKOUT"
                })

        except Exception:
            continue

        progress.progress((i + 1) / total)

    if results:
        st.success(f"Found {len(results)} lotto setups")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("No lotto setups found.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Penny Lotto Mode")
