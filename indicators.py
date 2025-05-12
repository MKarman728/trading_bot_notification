import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


def bollinger_bands(df: pd.DataFrame, plot=False, window=20):
    stock = pd.DataFrame()
    stock["Close"] = df["Close"]
    stock["rolling_mean"] = df["Close"].rolling(window).mean()
    stock["upper_band"] = stock["rolling_mean"] + 2 * df["Close"].rolling(window).std()
    stock["lower_band"] = stock["rolling_mean"] - 2 * df["Close"].rolling(window).std()
    stock = stock.tail(30)
    if plot:
        gen_plot(stock)
    if stock["Close"].iloc[-1] < stock["lower_band"].iloc[-1]:
        return "Buy"
    elif stock["Close"].iloc[-1] > stock["upper_band"].iloc[-1]:
        return "Sell"
    else:
        return np.nan


def gen_plot(df: pd.DataFrame):
    plt.figure(figsize=(12, 6))
    plt.plot(df["Close"], label="Close Price")
    plt.plot(df["rolling_mean"], label="Rolling_mean")
    plt.plot(df["upper_band"], label="upper_band")
    plt.plot(df["lower_band"], label="lower_band")
    plt.title("Indicator Data")
    plt.xlabel("Date")
    plt.ylabel("Prices")
    plt.legend()
    plt.show()


data = yf.Ticker("MSFT")
df = data.history(period="3mo")
print(bollinger_bands(df, plot=True))
