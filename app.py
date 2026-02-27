import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

st.set_page_config(page_title="Uilkie Yahoo Chaos Engine", layout="wide")
st.title("🚀 Uilkie Penny Lotto Chaos Engine — Yahoo Mode")

eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)

# -----------------------------
# STEP 1: Pull Yahoo Market Movers
# -----------------------------

def get_yahoo_movers():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
    params = {
        "scrIds": "day_gainers",
        "count": 50
    }
    r = requests.get(url, params=params)
    data = r.json()
    quotes = data["finance"]["result"][0]["quotes"]
    return [q["symbol"] for q in quotes]

try:
    movers = get_yahoo_movers()
except:
    st.error("Failed to pull Yahoo movers.")
    st.stop()

if not movers:
    st.info("No movers returned.")
    st.stop()

# -----------------------------
# STEP 2: Filter Under $5
# -----------------------------

candidates = []

for symbol in movers:
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.history(period="1d")["Close"].iloc[-1]
        if 0.20 <= price <= 5:
            candidates.append(symbol)
    except:
        continue

if not candidates:
    st.info("No lotto candidates under $5.")
    st.stop()

# -----------------------------
# STEP 3: Breakout + Volume Acceleration
# -----------------------------

chaos_hits = []

for symbol in candidates[:20]:
    try:
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
        if data.empty or len(data) < 6:
            continue

        data["AvgVol"] = data["Volume"].rolling(5).mean()

        latest = data.iloc[-1]
        previous = data.iloc[:-1]

        breakout = latest["High"] > previous["High"].max()
        vol_spike = latest["Volume"] > (latest["AvgVol"] * 3)
        expansion = (latest["Close"] - latest["Open"]) / latest["Open"] > 0.03

        if breakout and vol_spike and expansion:
            chaos_hits.append({
                "Ticker": symbol,
                "Price": round(latest["Close"], 3),
                "5m Move %": round(((latest["Close"] - latest["Open"]) / latest["Open"]) * 100, 2),
                "Volume": int(latest["Volume"])
            })

    except:
        continue

# -----------------------------
# DISPLAY
# -----------------------------

if chaos_hits:
    st.success("🚨 CHAOS BREAKOUT DETECTED")
    st.dataframe(pd.DataFrame(chaos_hits))
else:
    st.info("No confirmed breakouts right now.")

st.markdown("---")
st.caption("Yahoo Finance Powered | Free Mode | Breakout + Volume Engine")
