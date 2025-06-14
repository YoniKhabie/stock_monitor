from typing import Dict, List


def format_number(num):
    if isinstance(num, (int, float)):
        return f"{num:,.2f}"
    return num 

def precentage_to_close(data:Dict) -> List[str]:
    close = data["Close"]
    res = []
    for key, value in data.items():
        if(key == "Close" or value == None):
            continue
        val = ((value / close) -1) * 100
        val = round(abs(val),2)
        # val = val - 1 if val > 1 else val
        res.append(f"{key}: {val}%")
    return res

# def main():
# # TESTING
#     data = {
#         "Resistance": 6070,
#         "Close": 5976,
#         "Support":5948,
#         "SMA20": 5944,
#         "SMA94": 5945
#     }
#     res = precentage_to_close(data)
#     print(res)

# if __name__ == "__main__":
#     main()