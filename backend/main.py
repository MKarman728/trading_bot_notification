from datetime import datetime
from io import StringIO
import requests
import yfinance as yf
import pandas as pd
from indicators import bollinger_bands
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import TradingDatabase
from models import User
import os

# load dotenv files
load_dotenv()

# Sets up FastAPI end points
app = FastAPI()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users")
def create_user(user: User):
    """Add a new user to database"""
    trade_db = TradingDatabase()
    try:
        trade_db.add_users(
            email=user.email,
            name=user.name,
            image=user.image,
            provider=user.provider,
            provider_id=user.provider_id,
        )
        return {"success": True, "message": f"User {user.email} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Collects all of the S&P 500 stocks and determines what's a good buy and sell
@app.get("/bollinger_bands")
def main():
    # Instantiate the database
    trade_db = TradingDatabase()

    # Check if data has already been run today
    todays_signals = trade_db.get_day_signal()
    if todays_signals:
        print(f"Found {len(todays_signals)} existing signals for today")
        signals_df = pd.DataFrame(
            todays_signals, columns=["symbol", "security", "signal", "signal_date"]
        )
        return signals_df
    print("No signals found for today. Running analysis")

    # SP500 list
    url = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    tables = pd.read_html(StringIO(html), attrs={"id": "constituents"})
    df = tables[0]
    stocks = df[["Symbol", "Security"]].copy()
    stocks.columns = ["symbol", "security"]
    stocks["signal_date"] = "None"
    stocks["strategy"] = "Bollinger"
    for index, stock in stocks.iterrows():
        try:
            data = yf.Ticker(stock.loc["symbol"]).history(period="3mo")
            if data.empty or "Close" not in data.columns:
                signal = "No Data"
            else:
                signal = bollinger_bands(data)
        except Exception as e:
            print(f"Error on {stock['Symbol']}:{e}")
            signal = "Error"
        stocks.loc[index, "signal"] = signal
        stocks.loc[index, "signal_date"] = datetime.now().strftime("%Y-%m-%d")
    buy_sell_signals = stocks[
        (stocks["signal"] == "Buy") | (stocks["signal"] == "Sell")
    ]
    trade_db.save_signals(buy_sell_signals)
    return buy_sell_signals


if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    todays_stocks = main()
    print(todays_stocks)
