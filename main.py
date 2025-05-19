import yfinance as yf
import pandas as pd
from indicators import bollinger_bands
from dotenv import load_dotenv
from twilio.rest import Client
import os


load_dotenv()


def send_SMS(msg_text):
    account_sid = os.environ["ACCOUNT_SID"]
    auth_token = os.environ["AUTH_TOKEN"]
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_="+19494315225", body=msg_text, to="+16614443787"
    )
    return message


# Collects all of the S&P 500 stocks and determines what's a good buy and sell
def main():
    url = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    stocks = df[["Symbol", "Security"]].copy()
    stocks["Bollinger"] = "None"
    for index, stock in stocks.iterrows():
        try:
            data = yf.Ticker(stock.loc["Symbol"]).history(period="3mo")
            if data.empty or "Close" not in data.columns:
                signal = "No Data"
            else:
                signal = bollinger_bands(data)
        except Exception as e:
            print(f"Error on {stock['Symbol']}:{e}")
            signal = "Error"
        stocks.loc[index, "Bollinger"] = signal
    buy_sell_signals = stocks[(stocks["Bollinger"] == "Buy")]
    buy_sell_string = buy_sell_signals.to_string(index=False)
    send_SMS(buy_sell_string)
    return buy_sell_signals


if __name__ == "__main__":
    stocks = main()
    print(stocks)
