# pip install -r requirements.txt
import asyncio

from message import message_generator
from Stock.data import StockData
from Stock.img_generator import ImgGenerator
from telegram_bot import MyBot


async def main():
    bot = MyBot()
    try:
        ticker, period_days, interval = "^GSPC", 500, "1d"
        analyzer = StockData(ticker, period_days, interval)
        analyzer.analyze_pipline()

        message = message_generator(analyzer)


        img = ImgGenerator.run(analyzer)
        await bot.send_img_to_group(img, caption=message)
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())