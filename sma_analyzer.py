import asyncio

import yfinance as yf

from constants import TICKERS
from telegram_bot import MyBot


def get_total_stocks_sma(tickers = TICKERS):
    """
    Calculate the percentage of stocks trading above their 20-day SMA
    
    Args:
        tickers: List of stock ticker symbols
        
    Returns:
        float: Percentage of stocks above their 20-day SMA (rounded to 1 decimal)
    """
    # Download data
    df = yf.download(tickers, period="1mo", interval="1d", group_by='ticker', progress=False, threads=False)
    
    # Process data
    if not df.empty and 'Close' in df.columns.levels[1]:
        closes = df.xs('Close', axis=1, level=1, drop_level=True)
        smas = closes.rolling(20).mean().ffill()
        
        # Calculate stats
        valid_pairs = (~closes.iloc[-1].isna()) & (~smas.iloc[-1].isna())
        above_sma = (closes.iloc[-1] > smas.iloc[-1]).sum()
        percentage = (above_sma / valid_pairs.sum()) * 100 if valid_pairs.sum() > 0 else 0
        
        percentage = round(percentage, 2)
        return f"S5TW 20 SMA: {percentage}%"
    return f"S5TW 20 SMA: Error"

async def main():
    bot = MyBot()
    try:
        message = get_total_stocks_sma()
        await bot.send_message_to_group(message)
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())