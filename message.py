from datetime import datetime

import pytz

from helpers import format_number, precentage_to_close
from sma_analyzer import get_total_stocks_sma
from Stock.data import StockData


def message_generator(analyzer:StockData):
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
        message+=f"\n{get_total_stocks_sma()}"
        message+=f"\nPrices from close:"

        close_distance_arr = precentage_to_close(data)
        for distance in close_distance_arr:
            message+=f"\n{distance}"

        return message