# pip install -r requirements.txt

import asyncio
import threading
import time

import yfinance as yf

from indicators import bollinger, sma
from telegram_bot import send_message_to_group


class Stock:
    def __init__(self, ticker:str):
        self.ticker = ticker
        self.lock = threading.Lock()
        self.fetch_stock()

    def fetch_stock(self):
        self.df_daily = yf.download(self.ticker, interval="1d", period="1y", auto_adjust=True)
        self.df_inner_daily = yf.download(self.ticker, interval="30m", period="1mo", auto_adjust=True)
        self.__add_indecators()
        self.df_inner_daily = self.df_inner_daily.rename(columns={"Datetime": "Date"})
        return self.df_inner_daily

    def __add_indecators(self):
        for df in [self.df_daily, self.df_inner_daily]:
            sma(df, 6)
            sma(df, 50)
            sma(df, 200)
            bollinger(df, window=20)

            df.reset_index(inplace=True)

    def run_polling(self, interval=900, is_background_running=False):
        def poll():
            while True:
                print(f"[{time.ctime()}] Fetching new data for {self.ticker}...")
                try:
                    with self.lock:
                        self.fetch_stock()
                    print(f"[{time.ctime()}] Data updated successfully.")
                    print(self.df_inner_daily.head())

                except Exception as e:
                    print(f"[{time.ctime()}] Error updating data: {e}")
                time.sleep(interval)

        thread = threading.Thread(target=poll, daemon=is_background_running)
        thread.start()

ticker = "SPY"
stock = Stock(ticker)
data = stock.fetch_stock().head()
# stock.run_polling(2)
message = f"Last {ticker} Price is {data['Close'][ticker][0]}"
asyncio.run(send_message_to_group(message))