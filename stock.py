# pip install -r requirements.txt

import asyncio
import threading
import time

import yfinance as yf

from github_logger import log_notice, log_warning
from indicators import add_resistance, add_support, sma
from telegram_bot import send_message_to_group


class Stock:
    def __init__(self, ticker:str):
        self.ticker = ticker
        self.lock = threading.Lock()
        self.fetch_stock()

    ###### private methods ######

    def __add_indecators(self):
        for df in [self.df_daily, self.df_inner_daily]:
            sma(df, 6)
            sma(df, 50)
            sma(df, 200)
            df.reset_index(inplace=True)
            add_support(df)
            add_resistance(df)

    ###### public methods ######

    def fetch_stock(self):
        self.df_daily = yf.download(self.ticker, interval="1d", period="1y", auto_adjust=True)
        self.df_inner_daily = yf.download(self.ticker, interval="30m", period="1mo", auto_adjust=True, end="2025-05-30")

        # fixing cols
        self.df_daily.columns = self.df_daily.columns.droplevel(1)
        self.df_inner_daily.columns = self.df_inner_daily.columns.droplevel(1)

        # adding indicators
        self.__add_indecators()
        self.df_inner_daily = self.df_inner_daily.rename(columns={"Datetime": "Date"})
        return self.df_inner_daily

    def last_completed_price(self, col='Close', i=2):   
        return float(self.df_inner_daily[col].iloc[-i])

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

    def cross_check(self, fast='SMA6', slow='SMA50'):
        """
        checking if we have golden cross / death cross
        return: str, "1" for golden cross, "-1" for death cross, "0" for nothing
        """
        fast_after = self.last_completed_price(col=fast)
        slow_after = self.last_completed_price(col=slow)
        fast_before = self.last_completed_price(col=fast, i=3)
        slow_before = self.last_completed_price(col=slow, i=3)

        if fast_after > slow_after and fast_before < slow_before:
            return "1"
        if slow_after > fast_after and slow_before < fast_before:
            return "-1"
        return "0"
    
ticker = "SPY"
stock = Stock(ticker)
last_price = f"{stock.last_completed_price():.2f}"
message = "No cross found"
# print(stock.df_inner_daily.to_string())
if stock.cross_check() == "1":
    message = f"Found golden cross {ticker} Price is {last_price}"
    asyncio.run(send_message_to_group(message))
elif stock.cross_check() == "-1":
    message = f"Found death cross {ticker} Price is {last_price}"
    asyncio.run(send_message_to_group(message))
else:
    log_warning(message)
