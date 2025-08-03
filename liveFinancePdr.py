import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Define tickers ---
tickersDict = {
    "SP500": "^GSPC",
    "Bitcoin": "BTC-USD",
    "USDNOK": "USDNOK=X",
    "Oslo Børs": "OSEBX.OL",
    "Kongsberg Gruppen": "KOG.OL",
    "Europris": "EPR.OL",
    "SATS": "SATS.OL"
}

names = list(tickersDict.keys())
symbols = list(tickersDict.values())

# --- Time Windows ---
today = datetime.today()
start_30d = today - timedelta(days=30)
start_ytd = datetime(today.year, 1, 2)

# --- Fetch Data ---
st.info("📡 Fetching financial data...")
try:
    data = yf.download(
        tickers=symbols,
        start=start_ytd.strftime("%Y-%m-%d"),
        end=today.strftime("%Y-%m-%d"),
        group_by="ticker",
        progress=False,
        auto_adjust=True
    )
except Exception as e:
    st.error(f"❌ Failed to download data: {e}")
    st.stop()

if data.empty:
    st.warning("⚠️ No data returned from Yahoo Finance.")
    st.stop()

# --- Parse & Calculate ---
rows = []

for name, symbol in tickersDict.items():
    try:
        df = data[symbol] if isinstance(data.columns, pd.MultiIndex) else data
        if df.empty or "Close" not in df.columns:
            raise ValueError("Missing 'Close' prices")

        current = df["Close"].iloc[-1]
        previous = df["Close"].iloc[-2] if len(df) >= 2 else None

        # ✅ Updated: 30-day return based on last available business day before or on that date
        mask_30d = df.index <= pd.to_datetime(start_30d)
        price_30d_ago = df.loc[mask_30d]["Close"].iloc[-1] if mask_30d.any() else None

        price_ytd = df["Close"].iloc[0]

        return_1d = (current / previous - 1) * 100 if previous else None
        return_30d = (current / price_30d_ago - 1) * 100 if price_30d_ago else None
        return_ytd = (current / price_ytd - 1) * 100 if price_ytd else None

        rows.append({
            "Name": nam
