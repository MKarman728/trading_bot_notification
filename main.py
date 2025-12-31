from datetime import datetime, date
from io import StringIO
import requests
import yfinance as yf
import pandas as pd
from indicators import bollinger_bands
from dotenv import load_dotenv
import os
from fastapi import FastAPI
import sqlite3


# Sets up FastAPI end points
app = FastAPI()

# Creates database if it doesn't already exist
database_connect = sqlite3.connect("trades.db")

load_dotenv()


class TradingDatabase:
    def __init__(self, db_path="trades.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initializes database for trading signals if not already initialized"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create Tables with cursor
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        symbol VARCHAR(10) NOT NULL,
                        security VARCHAR(255),
                        signal VARCHAR(20) NOT NULL,
                        signal_date DATETIME DEFAULT (date('now')),
                        strategy VARCHAR(50) DEFAULT 'Bollinger'
                       )
                       """)
        conn.commit()
        conn.close()

    def save_signals(self, signals_df):
        """Saves signals to trading database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT symbol, date(signal_date) as signal_date
                       FROM signals
                       """)
        existing = set((row[0], row[1]) for row in cursor.fetchall())
        new_signals = []
        for _, row in signals_df.iterrows():
            signal_date = pd.to_datetime(row["signal_date"]).strftime("%Y-%m-%d")
            if (row["symbol"], signal_date) not in existing:
                new_signals.append(row)

        # Bulk insert all new signals into database
        if new_signals:
            new_df = pd.DataFrame(new_signals)
            new_df.to_sql("signals", conn, if_exists="append", index=False)
            print(
                f"Inserted {len(new_signals)} new signals, skipped {len(signals_df) - len(new_signals)} duplicates"
            )
        else:
            print("No new signals to insert (all duplicates)")
        conn.close()

    def day_signal(self, signal_date=None):
        if signal_date is None:
            signal_date = date.today().isoformat()
        else:
            signal_date = pd.to_datetime(signal_date).strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
                        SELECT symbol, security, signal, signal_date
                        FROM signals
                        WHERE signal_date = ? 
                       """,
                        (signal_date,)
                       )
        date_signal = cursor.fetchall()
        conn.close()
        return date_signal 


# Collects all of the S&P 500 stocks and determines what's a good buy and sell
@app.get("/bollinger_bands")
def main():
    #Instantiate the database
    trade_db = TradingDatabase()
    
    #Check if data has already been run today
    todays_signals = trade_db.day_signal()
    if todays_signals:
        print(f"Found {len(todays_signals)} existing signals for today")
        signals_df = pd.DataFrame(todays_signals, columns = ['symbol', 'security', 'signal', 'signal_date'])
        return signals_df
    print("No signals found for today. Running analysis")

    #SP500 list
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
