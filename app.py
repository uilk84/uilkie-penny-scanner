import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("Live Yahoo Top Gainers | Price < $10 | Momentum Breakouts")

# -----------------------------
# Get Yahoo Top Gainers
# -----------------------------

@st.cache_data(ttl=300)
def get_top_gainers():
    url = "https://finance.yahoo.com/markets/stocks/gainers/"
    tables = pd.read_html(url)
    df = tables[0]
    return df["Symbol"].dropna().tolist()

# -----------------------------
# RSI Function
# -----------------------------

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# -----------------------------
# Scanner
# -----------------------------

if st.button("Run Lotto Scan"):

    tickers = get_top_gainers()
    results = []
    progress = st.progress(0)
    total = len(tickers)

    for i, ticker in enumerate(tickers):
        try:
            df = yf.download(ticker, period="1mo", interval="1d", progress=False)

            if df.empty or len(df) < 20:
                continue

            price = df["Close"].iloc[-1]

            # Penny filter
            if price > 10:
                continue

            volume = df["Volume"].iloc[-1]
            avg_volume = df["Volume"].rolling(20).mean().iloc[-1]
            rel_volume = volume / avg_volume if avg_volume > 0 else 0

            rsi = calculate_rsi(df["Close"]).iloc[-1]

            high_5 = df["High"].rolling(5).max().iloc[-2]
            breakout = price > high_5

            if breakout and rel_volume > 1.5 and rsi > 50:
                results.append({
                    "Ticker": ticker,
                    "Price": round(float(price), 2),
                    "RSI": round(float(rsi), 2),
                    "Rel Volume": round(float(rel_volume), 2),
                    "Signal": "🚀 LOTTO MOMENTUM"
                })

        except:
            continue

        progress.progress((i + 1) / total)

    if results:
        st.success(f"Found {len(results)} lotto setups")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("No lotto setups found.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Live Gainers Mode")
