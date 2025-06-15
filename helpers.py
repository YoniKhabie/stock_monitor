import re
from typing import Dict, List


def format_value(value: str) -> str:
    # Match number and optional suffix like (3.73%)
    match = re.match(r"([-+]?\d*\.?\d+)(.*)", value)
    if match:
        number_part = float(match.group(1))
        suffix = match.group(2)
        return f"{number_part:,.2f}{suffix}"
    return value  # fallback if it doesn't match


def format_number(num) -> str:
    if isinstance(num, (int, float)):
        return f"{num:,.2f}"
    return str(num) 

def precentage_to_close(data: Dict[str, float]) -> Dict[str, str]:
    close = data["Close"]
    for key, value in list(data.items()):
        if key == "Close" or value is None:
            continue
        percentage = ((value / close) - 1) * 100
        percentage = round(percentage, 2)
        data[key] = f"{value} ({percentage}%)"
    # Optionally format Close as well:
    data["Close"] = f"{close}"
    return data

# def main():
# # TESTING
#     data = {
#         "Resistance": 6070.999,
#         "Close": 5976,
#         "Support":5948,
#         "SMA20": 5944,
#         "SMA94": 5945
#     }
    
#     precentage_to_close(data)

# if __name__ == "__main__":
#     main()