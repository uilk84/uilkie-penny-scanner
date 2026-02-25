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
            if price > 10:
                continue

            avg_volume = df["Volume"].rolling(20).mean().iloc[-1]

            # Relative volume spike
            rel_volume = volume / avg_volume if avg_volume > 0 else 0

            # RSI
            rsi = calculate_rsi(df["Close"]).iloc[-1]

            # 5-day breakout (more aggressive)
            high_5 = df["High"].rolling(5).max().iloc[-2]
            breakout = price > high_5

            # Aggressive lotto logic
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
