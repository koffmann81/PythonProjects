import yfinance as yf

#tickers = ["^GSPC", "BTC-USD", "USDNOK=X"]
tickersDict = {"SP500":"^GSPC", "Bitcoin":"BTC-USD", "USDNOK":"USDNOK=X", "Oslo Børs":"OSEBX.OL"}
tickers=list(tickersDict.values())
current_price = []
company=yf.Ticker(tickers[0])
cp=company.info["regularMarketPrice"]

for i in range(len(tickers)):
    company = yf.Ticker(tickers[i])
    print(company)
    current_price.append(company.info["regularMarketPrice"])
print(current_price)

