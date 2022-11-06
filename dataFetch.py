import streamlit as st
import databutton as db
import yfinance as yf



st.title("Selected Financials data")
dataList={"SP500":"^GSPC", "Bitcoin":"BTC-USD"}
tickers=st.multiselect("Select tickers", dataList.keys(),dataList.keys())
st.write(tickers)
st.write("Showing historical prices")
tickerList=[dataList[x] for x in tickers]
yTickers=tickerList[0]
#if len(tickerList)>1:
#    for i in tickerList:
 #       yTickers=yTickers.append(" "+tickerList[i+1])
#else:
#    yTickers=tickerList


yTickers=tickerList[0]+" "+tickerList[1]
data=yf.Tickers(yTickers)


data=data.history(period="5d")["Close"]
st.dataframe(data)






# Fetch a dataframe from databutton
# If they key doesn't exist you'll get an empty dataframe
#st.dataframe(db.storage.dataframes.get("my-test-data"))

# Go ahead and remove the hashtag (#) from the line below to get some balloons
#st.balloons()