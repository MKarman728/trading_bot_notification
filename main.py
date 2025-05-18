import yfinance as yf
import pandas as pd
from indicators import bollinger_bands

# Collect the S&P 500 stocks

data = yf.Ticker("MSFT")
df = data.history(period="3mo")
print(bollinger_bands(df, plot=True))
