import yfinance as yf
import numpy as np
#tickers = ["^GSPC", "BTC-USD", "USDNOK=X"]
tickersDict = {"SP500":"^GSPC", "Bitcoin":"BTC-USD", "USDNOK":"USDNOK=X", "Oslo Børs":"OSEBX.OL"}
tickers=list(tickersDict.values())
current_price = []
returns=[]
company=yf.Ticker(tickers[0])
cp=company.info["regularMarketPrice"]
cp2=company.info
cp2Return=company.info["regularMarketPrice"]/company.info["regularMarketPreviousClose"]-1


for i in range(len(tickers)):
    company = yf.Ticker(tickers[i])
    print(company)
    current_price.append(company.info["regularMarketPrice"])
    returnSec="{:.2f}".format((company.info["regularMarketPrice"]/company.info["regularMarketPreviousClose"]-1)*100)+"%"
    returns.append(returnSec)
    #returns.append(company.info["regularMarketPrice"]/company.info["regularMarketPreviousClose"]-1)
print(current_price)
print(returns)

