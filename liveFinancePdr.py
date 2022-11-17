import pandas_datareader as web
import streamlit as st
import pandas as pd

#tickers = ["MSFT", "BTC-USD", "^GSPC", "EURUSD=X"]

#current_price = web.get_quote_yahoo(tickers)["regularMarketPrice"]
#print(web.get_quote_yahoo(tickers))
#a=web.get_quote_yahoo(tickers) 84 columns

tickersDict = {"SP500":"^GSPC", "Bitcoin":"BTC-USD", "USDNOK":"USDNOK=X", "Oslo Børs":"OSEBX.OL"}
tickers=list(tickersDict.values())
names=st.multiselect("Select tickers", tickersDict.keys(),list(tickersDict.keys()))
tickerList=[tickersDict[x] for x in names]

current_price =web.get_quote_yahoo(tickers)["regularMarketPrice"]
previous_close=web.get_quote_yahoo(tickers)["regularMarketPreviousClose"]
returns=list((current_price/previous_close-1)*100)
returns=["%.2f" % elem for elem in returns]
returns=[elem+"%" for elem in returns]
#returns="{:.2f}".format(returns)

#Creating a dataframe with names and price
data_tuple=list(zip(names,current_price, returns))
df=pd.DataFrame(data_tuple, columns=["Name", "Price", "Return 1-day"])
df=df.set_index("Name")

st.dataframe(df.style.format({"Price":"{:.1f}"}))

company=tickers[0]
#cp=company.info["regularMarketPrice"]
#cp2=company.info
cp2Return=web.get_quote_yahoo(tickers)["regularMarketPrice"]/web.get_quote_yahoo(tickers)["regularMarketPreviousClose"]-1