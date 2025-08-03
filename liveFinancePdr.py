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

# Timeframes
today = datetime.today()
start_30d = today - timedelta(days=30)
start_ytd = datetime(today.year, 1, 2)  # 1 Jan may be a holiday

# Initialize data holders
data_rows = []

# Fetch and compute returns
for name, symbol in tickersDict.items():
    try:
        hist = yf.download(symbol, start=start_ytd.strftime("%Y-%m-%d"), end=today.strftime("%Y-%m-%d"), progress=False)
        if hist.empty or "Close" not in hist:
            raise ValueError("No data")

        current = hist["Close"][-1]
        previous = hist["Close"][-2] if len(hist) >= 2 else None
        price_30d_ago = hist.loc[hist.index >= pd.to_datetime(start_30d)].iloc[0]["Close"] if len(hist.loc[hist.index >= pd.to_datetime(start_30d)]) > 0 else None
        price_ytd = hist.iloc[0]["Close"]

        # Calculate returns
        daily_return = ((current / previous) - 1) * 100 if previous else None
        return_30d = ((current / price_30d_ago) - 1) * 100 if price_30d_ago else None
        return_ytd = ((current / price_ytd) - 1) * 100 if price_ytd else None

        data_rows.append({
            "Name": name,
            "Price": current,
            "Return 1-day": f"{daily_return:.2f}%" if daily_return is not None else "N/A",
            "Return 30-day": f"{return_30d:.2f}%" if return_30d is not None else "N/A",
            "Return YTD": f"{return_ytd:.2f}%" if return_ytd is not None else "N/A"
        })

    except Exception as e:
        data_rows.append({
            "Name": name,
            "Price": "Error",
            "Return 1-day": "Error",
            "Return 30-day": "Error",
            "Return YTD": "Error"
        })

# Convert to DataFrame
df = pd.DataFrame(data_rows).set_index("Name")

# ---- STREAMLIT APP ----
st.title("📈 Financial Prices and Returns")

selectedTickers = st.multiselect("Select tickers", df.index.tolist(), df.index.tolist())
filtered_df = df.loc[selectedTickers]

st.dataframe(filtered_df.style.format({"Price": "{:.2f}"}))
