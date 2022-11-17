import streamlit as st
import databutton as db
import yfinance as yf
import numpy as np
import pandas as pd


st.title("Live Prices")
tickerDict={"SP500":"^GSPC", "Bitcoin":"BTC-USD",
"USDNOK":"USDNOK=X", "Oslo Børs":"OSEBX.OL"}
names=st.multiselect("Select tickers", tickerDict.keys(),list(tickerDict.keys())[:2])
tickers=list(tickerDict.values())
#st.write(tickers)
tickerList=[tickerDict[x] for x in names]
#st.write(tickerList)
current_price=[]

for i in range(len(tickerList)):
    company = yf.Ticker(tickerList[i])
    current_price.append(company.info["regularMarketPrice"])

#Rounding to no decimals
#price_array=np.array(current_price)
#rounded_prices=np.around(price_array,0)
#current_price=list(rounded_prices)

#st.write(current_price)

#Creating a dataframe with names and price
data_tuple=list(zip(names,current_price))

df=pd.DataFrame(data_tuple, columns=["Name", "Price"])
#Hide index
#hide_dataframe_row_index = """
            #<style>
            #.row_heading.level0 {display:none}
            #.blank {display:none}
            #</style>
            #"""
#st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

#st.table(df.style.format({"Price":"{:.1f}"}))
df=df.set_index("Name")

st.dataframe(df.style.format({"Price":"{:.1f}"}))



# Fetch a dataframe from databutton
# If they key doesn't exist you'll get an empty dataframe
#st.dataframe(db.storage.dataframes.get("my-test-data"))

# Go ahead and remove the hashtag (#) from the line below to get some balloons
#st.balloons()