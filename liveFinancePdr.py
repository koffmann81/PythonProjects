import yfinance as yf
import streamlit as st
import pandas as pd

# Define tickers
tickersDict = {
    "SP500": "^GSPC",
    "Bitcoin": "BTC-USD",
    "USDNOK": "USDNOK=X",
    "Oslo Børs": "OSEBX.OL"
}

names = list(tickersDict.keys())
tickers = list(tickersDict.values())

# Fetch data using yfinance
price_data = {}
returns = {}

for name, symbol in tickersDict.items():
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current = info.get("regularMarketPrice", None)
        previous = info.get("regularMarketPreviousClose", None)

        if current is not None and previous is not None:
            daily_return = (current / previous - 1) * 100
            price_data[name] = current
            returns[name] = f"{daily_return:.2f}%"
        else:
            price_data[name] = "N/A"
            returns[name] = "N/A"
    except Exception as e:
        price_data[name] = "Error"
        returns[name] = "Error"

# Build dataframe
df = pd.DataFrame({
    "Name": list(price_data.keys()),
    "Price": list(price_data.values()),
    "Return 1-day": list(returns.values())
})
df = df.set_index("Name")

# ---- STREAMLIT APP ----
st.title("📈 Financial Prices and Returns")

selectedTickers = st.multiselect("Select tickers", df.index.tolist(), df.index.tolist())
filtered_df = df.loc[selectedTickers]

st.dataframe(filtered_df.style.format({"Price": "{:.2f}"}))
