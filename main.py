from io import StringIO
import requests
import yfinance as yf
import pandas as pd
from indicators import bollinger_bands
from dotenv import load_dotenv
import os

load_dotenv()


def send_SMS(msg_text):
    account_sid = os.environ["ACCOUNT_SID"]
    auth_token = os.environ["AUTH_TOKEN"]
    msg_sid = os.environ["MESSAGE_SERVICE_SID"]
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        messaging_service_sid=msg_sid, body=msg_text, to="+16614443787"
    )
    return message


def send_email(msg_text):
    message = Mail(
        from_email="mkarman08@gmail.com",
        to_emails=["mkarman08@gmail.com", "mduong513@gmail.com"],
        subject="Stock Market Tickers",
        html_content=f"<p>{msg_text}</p>",
    )
    try:
        sg = SendGridAPIClient(os.environ.get("EMAIL_API"))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))
        return msg_text


# Collects all of the S&P 500 stocks and determines what's a good buy and sell
def main():
    url = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    tables = pd.read_html(StringIO(html), attrs={"id": "constituents"})
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
    buy_sell_signals = stocks[
        (stocks["Bollinger"] == "Buy") | (stocks["Bollinger"] == "Sell")
    ]
    buy_sell_string = "<br><br>".join(
        buy_sell_signals.apply(
            lambda row: f"Symbol: {row['Symbol']} Security: {row['Security']} Signal: {row['Bollinger']}",
            axis=1,
        )
    )
    # send_email(buy_sell_string)
    return buy_sell_signals


if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    stocks = main()
    print(stocks)
