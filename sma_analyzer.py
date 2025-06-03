import asyncio

import yfinance as yf

from constants import TICKERS
from telegram_bot import send_message_to_group


def get_percentage_above_sma(tickers = TICKERS):
    """
    Calculate the percentage of stocks trading above their 20-day SMA
    
    Args:
        tickers: List of stock ticker symbols
        
    Returns:
        float: Percentage of stocks above their 20-day SMA (rounded to 1 decimal)
    """
    # Download data
    df = yf.download(tickers, period="1mo", interval="1d", group_by='ticker', progress=False)
    
    # Process data
    if not df.empty and 'Close' in df.columns.levels[1]:
        closes = df.xs('Close', axis=1, level=1, drop_level=True)
        smas = closes.rolling(20).mean().ffill()
        
        # Calculate stats
        valid_pairs = (~closes.iloc[-1].isna()) & (~smas.iloc[-1].isna())
        above_sma = (closes.iloc[-1] > smas.iloc[-1]).sum()
        percentage = (above_sma / valid_pairs.sum()) * 100 if valid_pairs.sum() > 0 else 0
        
        return round(percentage, 2)
    return 0.0

# percentage_above = get_percentage_above_sma()
# message = f"{percentage_above}% of stocks are above their 20-day SMA"
# asyncio.run(send_message_to_group(message))

try:
    percentage_above = get_percentage_above_sma()
    message = f"{percentage_above}% of stocks are above their 20-day SMA"
    asyncio.run(send_message_to_group(message))
except Exception as e:
    print(f"Error sending message: {e}")
    raise  # This will make the GitHub Action fail visibly

