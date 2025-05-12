import yfinance as yf
import pandas as pd

dat = yf.Ticker("MSFT")

print(dat.history(period="3mo"))
