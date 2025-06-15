from datetime import datetime

import pytz

from helpers import format_number, format_value, precentage_to_close
from sma_analyzer import get_total_stocks_sma
from Stock.data import StockData


def message_generator(analyzer: StockData):
    # Prices details
    sma_fast = round(analyzer.get_last("SMA_20"), 2)
    sma_slow = round(analyzer.get_last("SMA_94"), 2)
    close = round(analyzer.get_last("Close"), 2)
    key_levels = [round(p, 2) for p in analyzer.get_surrounding_key_levels()]
    support, resistance = key_levels[0], key_levels[1]
    gaps_list = analyzer.get_open_gaps()
    gaps_list[0].price_level
    gaps_list = [round(gap.gap_from,2) for gap in gaps_list]
    # add gaps to data
    data = {
        "Resistance": resistance,
        "Close": close,
        "Support": support,
        "SMA20": sma_fast,
        "SMA94": sma_slow
    }
    for index, gap in enumerate(gaps_list):
        data[f"Gap {len(gaps_list)- index}"] = gap

    # Inject percentages
    data = precentage_to_close(data)

    # Sort by original float values for consistency (strip % if needed for sorting)
    sorted_items = sorted(data.items(), key=lambda x: float(x[1].split()[0]), reverse=True)

    ny_timezone = pytz.timezone("America/New_York")
    current_time = datetime.now(ny_timezone).strftime("%d-%m-%Y %H:%M")       

    message = f"{current_time}\n" + "\n".join(
        f"{key}: {format_value(value)}" for key, value in sorted_items
    )
    message += f"\n{get_total_stocks_sma()}"
    # print(message)

    return message