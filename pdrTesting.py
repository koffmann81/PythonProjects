import pandas_datareader as web

tickers = ["MSFT", "BTC-USD", "^GSPC", "EURUSD=X"]

current_price = web.get_quote_yahoo(tickers)["regularMarketPrice"]
print(web.get_quote_yahoo(tickers))
a=web.get_quote_yahoo(tickers)
