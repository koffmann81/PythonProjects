import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Define tickers
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

# Time windows
today = datetime.today()
start_30d = today - timedelta(days=30)
start_ytd = datetime(today.year, 1, 2)

# Download all data at once
data = yf.download(
    tickers=symbols,
    start=start_ytd.strftime("%Y-%m-%d"),
    end=today.strftime("%Y-%m-%d"),
    group_by="ticker",
    progress=False,
    auto_adjust=True  # adjusted close prices
)

# Prepare output
rows = []

for name, symbol in tickersDict.items():
    try:
        df = data[symbol] if isinstance(data, dict) else data[symbol]
        if df.empty or "Close" not in df.columns:
            raise ValueError("No close data")

        current = df["Close"].iloc[-1]
        previous = df["Close"].iloc[-2] if len(df) >= 2 else None
        price_30d_ago = df[df.index >= pd.to_datetime(start_30d)]["Close"].iloc[0] if len(df[df.index >= pd.to_datetime(start_30d)]) > 0 else None
        price_ytd = df["Close"].iloc[0]

        return_1d = (current / previous - 1) * 100 if previous else None
        return_30d = (current / price_30d_ago - 1) * 100 if price_30d_ago else None
        return_ytd = (current / price_ytd - 1) * 100 if price_ytd else None

        rows.append({
            "Name": name,
            "Price": current,
            "Return 1-day": f"{return_1d:.2f}%" if return_1d is not None else "N/A",
            "Return 30-day": f"{return_30d:.2f}%" if return_30d is not None else "N/A",
            "Return YTD": f"{return_ytd:.2f}%" if return_ytd is not None else "N/A"
        })

    except Exception as e:
        rows.append({
            "Name": name,
            "Price": "Error",
            "Return 1-day": "Error",
            "Return 30-day": "Error",
            "Return YTD": "Error"
        })

#
