# pip install -r requirements.txt
import asyncio
from datetime import datetime

import pytz

from Stock.data import StockData
from Stock.img_generator import ImgGenerator
from telegram_bot import MyBot


def format_number(num):
    if isinstance(num, (int, float)):
        return f"{num:,.2f}"
    return num 

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
        support, resistance = key_levels[0], key_levels[1]
        data = {
            "Resistance": resistance,
            "Close": close,
            "Support":support,
            "SMA20": sma_fast,
            "SMA94": sma_slow
        }

        sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        ny_timezone = pytz.timezone("America/New_York")
        current_time = datetime.now(ny_timezone).strftime("%d-%m-%Y %H:%M")       
        message = f"{current_time}\n" + "\n".join(
            f"{key}: {format_number(value)}" for key, value in sorted_items
        )

        img = ImgGenerator.run(analyzer)
        await bot.send_img_to_group(img, caption=message)
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())