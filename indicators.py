import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


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
        return "No Signal"


def momentum(df: pd.DataFrame, plot=False, window=90):
    stocks = pd.DataFrame()
    stocks["Volume"] = df["Volume"]
    stocks["Average"] = df["Volume"].rolling(window).mean()
    stocks["Atypical"] = np.where(
        stocks["Volume"] > stocks["Average"], "Unusual", "Normal"
    )
    print(stocks.tail(90))


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


if __name__ == "__main__":
    data = yf.Ticker("MSFT").history(period="9mo")
    print(momentum(data, plot=True))
    # print(bollinger_bands(data, plot=True))
