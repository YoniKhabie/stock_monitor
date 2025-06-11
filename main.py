# pip install -r requirements.txt
import asyncio

from Stock.data import StockData
from Stock.img_generator import ImgGenerator
from telegram_bot import MyBot


async def main():
    bot = MyBot()
    try:
        ticker, period_days, interval = "^GSPC", 500, "1d"
        analyzer = StockData(ticker, period_days, interval)
        analyzer.analyze_pipline()

        # prices details
        sma_fast = round(analyzer.get_last("SMA_20"), 2)
        sma_slow = round(analyzer.get_last("SMA_94"), 2)
        close = round(analyzer.get_last("Close"), 2)
        key_levels = [round(p, 2) for p in analyzer.get_surrounding_key_levels()]
        # open_gaps = analyzer.get_open_gaps() later feature
        message = f"Close: {close}\nSMA20: {sma_fast}\nSMA94:{sma_slow}\nNext Support/Resistance Levels:{key_levels}"

        img = ImgGenerator.run(analyzer)
        await bot.send_img_to_group(img, caption=f"Here is the latest chart 📈\n{message}")
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())