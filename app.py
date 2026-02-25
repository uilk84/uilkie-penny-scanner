import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Uilkie Penny Lotto Scanner", layout="wide")

st.title("🚀 Uilkie Penny Lotto Scanner")
st.write("NASDAQ + NYSE | Price < $10 | Breakout + Momentum")

# --- Load NASDAQ + NYSE tickers ---
@st.cache_data
def load_tickers():
    nasdaq = pd.read_csv(
        "https://old.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
        sep="|"
    )
    nyse = pd.read_csv(
        "https://old.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",
        sep="|"
    )

    tickers = pd.concat([nasdaq["Symbol"], nyse["ACT Symbol"]])
    tickers = tickers.dropna().unique().tolist()
    return tickers

tickers = load_tickers()

# --- RSI Function ---
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# --- Scanner ---
results = []

run_scan = st.button("Run Lotto Scan")

if run_scan:
    progress = st.progress(0)
    total = len(tickers[:500])  # limit for speed (first 500)

    for i, ticker in enumerate(tickers[:500]):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo")

            if len(df) < 20:
                continue

            price = df["Close"].iloc[-1]
            volume = df["Volume"].iloc[-1]

            if price > 10 or volume < 500000:
                continue

            high_20 = df["High"].rolling(20).max().iloc[-2]
            breakout = price > high_20

            rsi = calculate_rsi(df["Close"]).iloc[-1]

            if breakout and rsi > 55:
                results.append({
                    "Ticker": ticker,
                    "Price": round(price, 2),
                    "RSI": round(rsi, 2),
                    "Volume": int(volume),
                    "Signal": "🚀 LOTTO BREAKOUT"
                })

        except:
            continue

        progress.progress((i + 1) / total)

    if results:
        st.success(f"Found {len(results)} lotto setups")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("No lotto setups found.")
