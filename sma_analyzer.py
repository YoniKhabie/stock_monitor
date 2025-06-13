import yfinance as yf

from constants import TICKERS


def get_total_stocks_sma(tickers = TICKERS):
    """
    Calculate the percentage of stocks trading above their 20-day SMA
    
    Args:
        tickers: List of stock ticker symbols
        
    Returns:
        float: Percentage of stocks above their 20-day SMA (rounded to 1 decimal)
    """
    # Download data
    df = yf.download(tickers, period="1mo", interval="1d", group_by='ticker', progress=True, threads=4, timeout=10)
    
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
