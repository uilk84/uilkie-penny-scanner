import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ----------------------------------
# Page Setup
# ----------------------------------

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("Full Market Mode | Ranked Momentum | API Safe")

# ----------------------------------
# Load S&P 500 Tickers (Safe Method)
# ----------------------------------

@st.cache_data(ttl=86400)
def get_sp500_tickers():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df = table[0]
    return df["Symbol"].tolist()

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

    tickers = get_sp500_tickers()
    tickers = tickers[:400]  # limit for stability

    results = []

    try:
        data = yf.download(
            tickers,
            period="5d",
            interval="1d",
            group_by="ticker",
            progress=False
        )
    except:
        st.error("Data download failed.")
        st.stop()

    for ticker in tickers:
        try:
            df = data[ticker]

            if df.empty or len(df) < 2:
                continue

            price = df["Close"].iloc[-1]
            prev_close = df["Close"].iloc[-2]

            percent_change = ((price - prev_close) / prev_close) * 100

            rsi = calculate_rsi(df["Close"]).iloc[-1]

            results.append({
                "Ticker": ticker,
                "Price": round(float(price), 2),
                "% Change": round(float(percent_change), 2),
                "RSI": round(float(rsi), 2)
            })

        except:
            continue

    df_results = pd.DataFrame(results)

    # Rank by % Change
    df_results = df_results.sort_values(by="% Change", ascending=False)

    # Apply Penny + Momentum Filters
    df_filtered = df_results[
        (df_results["Price"] < 10) &
        (df_results["% Change"] > 2) &
        (df_results["RSI"] > 45)
    ]

    if not df_filtered.empty:
        st.success(f"Found {len(df_filtered)} momentum setups")
        st.dataframe(df_filtered.head(20))
    else:
        st.warning("No momentum setups found.")

st.markdown("---")
st.caption("Uilkie Alpha Fund | Ranked Market Scanner")
